package com.qkraft.optimizer.service;

import com.qkraft.optimizer.dto.DiagramDtos.*;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class DdlParserService {

    public String normalizeDdl(String ddl) {
        if (ddl == null) return "";
        String text = ddl.trim();

        // 1. Convert Oracle/MySQL specific types to standard PostgreSQL/ANSI SQL
        text = text.replaceAll("(?i)\\bNUMBER\\s*\\(\\s*(\\d+)\\s*\\)", "INT");
        text = text.replaceAll("(?i)\\bNUMBER\\b", "INT");
        text = text.replaceAll("(?i)\\bVARCHAR2\\s*\\(\\s*(\\d+)\\s*\\)", "VARCHAR($1)");
        text = text.replaceAll("(?i)\\bVARCHAR2\\b", "VARCHAR(255)");
        text = text.replaceAll("(?i)\\bVARCAHR2?\\s*\\(\\s*\\)", "VARCHAR(255)");
        text = text.replaceAll("(?i)\\bVARCAHR2?\\b", "VARCHAR(255)");
        text = text.replaceAll("(?i)\\bDATETIME\\b", "TIMESTAMP");

        // 2. Ensure trailing semicolon
        if (!text.endsWith(";")) {
            text += ";";
        }
        text = text.replaceAll(";\\s*", ";\n\n");
        text = text.replaceAll("(?i)(CREATE\\s+TABLE[^(]+?\\()\\s*", "$1\n    ");

        StringBuilder sb = new StringBuilder();
        int parenDepth = 0;
        for (char c : text.toCharArray()) {
            if (c == '(') {
                parenDepth++;
                sb.append(c);
            } else if (c == ')') {
                parenDepth--;
                sb.append(c);
            } else if (c == ',' && parenDepth == 1) {
                sb.append(",\n    ");
            } else {
                sb.append(c);
            }
        }

        String res = sb.toString().replaceAll("([^\\n])\\s*\\);", "$1\n);");
        // Remove empty lines between column definitions
        res = res.replaceAll("(?m)^[ \t]*\r?\n", "");
        return res.trim();
    }

    public DiagramData parseDdlToDiagram(String ddl) {
        List<TableInfo> tables = new ArrayList<>();
        List<RelationInfo> relations = new ArrayList<>();

        if (ddl == null || ddl.trim().isEmpty()) {
            return new DiagramData(tables, relations);
        }

        String normalized = normalizeDdl(ddl);

        // Collect indexed columns
        Set<String> indexCols = new HashSet<>();
        Pattern idxPattern = Pattern.compile("(?i)CREATE\\s+(?:UNIQUE\\s+)?INDEX\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?([a-zA-Z0-9_]+)\\s+ON\\s+([a-zA-Z0-9_]+)\\s*\\(([^)]+)\\)");
        Matcher idxMatcher = idxPattern.matcher(normalized);
        while (idxMatcher.find()) {
            String tbl = idxMatcher.group(2).trim().toLowerCase();
            String[] cols = idxMatcher.group(3).split(",");
            for (String c : cols) {
                indexCols.add(tbl + "." + c.trim().toLowerCase());
            }
        }

        // Match table definitions (supporting with or without semicolon)
        Pattern tblPattern = Pattern.compile("(?i)CREATE\\s+TABLE\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?([a-zA-Z0-9_]+)\\s*\\(([\\s\\S]*?)\\)(?:\\s*;|\\s*$)");
        Matcher tblMatcher = tblPattern.matcher(normalized);

        while (tblMatcher.find()) {
            String tblName = tblMatcher.group(1).trim();
            String body = tblMatcher.group(2).trim();

            List<ColumnInfo> columns = new ArrayList<>();
            Set<String> pkCols = new HashSet<>();
            Map<String, String> fkCols = new HashMap<>();

            // Parse body elements respecting parens
            List<String> elements = new ArrayList<>();
            StringBuilder cur = new StringBuilder();
            int depth = 0;
            for (char ch : body.toCharArray()) {
                if (ch == '(') depth++;
                else if (ch == ')') depth--;
                else if (ch == ',' && depth == 0) {
                    elements.add(cur.toString().trim());
                    cur = new StringBuilder();
                    continue;
                }
                cur.append(ch);
            }
            if (cur.length() > 0) elements.add(cur.toString().trim());

            // 1. Detect constraints (PK, FK)
            for (String el : elements) {
                if (el.isEmpty()) continue;
                Matcher pkMatch = Pattern.compile("(?i)PRIMARY\\s+KEY\\s*\\(([^)]+)\\)").matcher(el);
                if (pkMatch.find() && !el.matches("(?i)^[a-zA-Z0-9_]+\\s+(INT|SERIAL|VARCHAR|TEXT).*")) {
                    for (String p : pkMatch.group(1).split(",")) {
                        pkCols.add(p.trim().toLowerCase());
                    }
                    continue;
                }

                Matcher fkMatch = Pattern.compile("(?i)FOREIGN\\s+KEY\\s*\\(([^)]+)\\)\\s*REFERENCES\\s+([a-zA-Z0-9_]+)\\s*(?:\\(([^)]+)\\))?").matcher(el);
                if (fkMatch.find()) {
                    String[] fks = fkMatch.group(1).split(",");
                    String refTbl = fkMatch.group(2).trim();
                    String refCol = fkMatch.group(3) != null ? fkMatch.group(3).trim() : "id";
                    for (String fk : fks) {
                        String cleanFk = fk.trim();
                        fkCols.put(cleanFk.toLowerCase(), refTbl + "(" + refCol + ")");
                        relations.add(new RelationInfo(tblName, cleanFk, refTbl, refCol));
                    }
                    continue;
                }
            }

            // 2. Parse Column definitions
            for (String el : elements) {
                if (el.matches("(?i)^(CONSTRAINT|PRIMARY|FOREIGN|CHECK|UNIQUE)\\b.*")) continue;
                Matcher colM = Pattern.compile("(?i)^([a-zA-Z0-9_]+)\\s+([a-zA-Z0-9_]+(?:\\s*\\([^)]*\\))?)").matcher(el);
                if (colM.find()) {
                    String cName = colM.group(1).trim();
                    String cType = colM.group(2).trim();

                    // Normalize type for diagram display
                    cType = cType.replaceAll("(?i)\\bNUMBER\\b", "INT");
                    cType = cType.replaceAll("(?i)\\bVARCHAR2\\b", "VARCHAR");

                    boolean isPk = pkCols.contains(cName.toLowerCase()) || el.toUpperCase().contains("PRIMARY KEY");
                    boolean isFk = fkCols.containsKey(cName.toLowerCase()) || el.toUpperCase().contains("REFERENCES");
                    String ref = fkCols.get(cName.toLowerCase());

                    if (!isFk) {
                        Matcher inlineRef = Pattern.compile("(?i)REFERENCES\\s+([a-zA-Z0-9_]+)\\s*(?:\\(([^)]+)\\))?").matcher(el);
                        if (inlineRef.find()) {
                            isFk = true;
                            String refTbl = inlineRef.group(1).trim();
                            String refCol = inlineRef.group(2) != null ? inlineRef.group(2).trim() : "id";
                            ref = refTbl + "(" + refCol + ")";
                            relations.add(new RelationInfo(tblName, cName, refTbl, refCol));
                        }
                    }

                    boolean isIndexed = isPk || indexCols.contains(tblName.toLowerCase() + "." + cName.toLowerCase());
                    columns.add(new ColumnInfo(cName, cType, isPk, isFk, ref, isIndexed));
                }
            }

            tables.add(new TableInfo(tblName, columns, 8));
        }

        return new DiagramData(tables, relations);
    }
}
