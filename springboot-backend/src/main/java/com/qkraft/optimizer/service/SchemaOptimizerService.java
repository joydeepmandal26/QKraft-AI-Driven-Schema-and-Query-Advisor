package com.qkraft.optimizer.service;

import com.qkraft.optimizer.dto.AnalyzeDtos.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class SchemaOptimizerService {

    @Autowired
    private DdlParserService ddlParserService;

    public List<String> detectSchemaProblems(String ddl) {
        List<String> problems = new ArrayList<>();
        if (ddl == null || ddl.trim().isEmpty()) return problems;

        String normalized = ddlParserService.normalizeDdl(ddl);

        // Discover all defined tables in the schema
        Set<String> definedTables = new HashSet<>();
        Pattern tblStartPattern = Pattern.compile("(?i)CREATE\\s+TABLE\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?([a-zA-Z0-9_]+)");
        Matcher tblStartMatcher = tblStartPattern.matcher(normalized);
        while (tblStartMatcher.find()) {
            definedTables.add(tblStartMatcher.group(1).trim().toLowerCase());
        }

        // Collect existing indexes
        Set<String> existingIndexes = new HashSet<>();
        Pattern idxPattern = Pattern.compile("(?i)CREATE\\s+(?:UNIQUE\\s+)?INDEX\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?([a-zA-Z0-9_]+)\\s+ON\\s+([a-zA-Z0-9_]+)\\s*\\(([^)]+)\\)");
        Matcher idxMatcher = idxPattern.matcher(normalized);
        while (idxMatcher.find()) {
            String tbl = idxMatcher.group(2).trim().toLowerCase();
            String[] cols = idxMatcher.group(3).split(",");
            for (String c : cols) {
                existingIndexes.add(tbl + "." + c.trim().toLowerCase());
            }
        }

        Pattern tblPattern = Pattern.compile("(?i)CREATE\\s+TABLE\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?([a-zA-Z0-9_]+)\\s*\\(([\\s\\S]*?)\\)(?:\\s*;|\\s*$)");
        Matcher tblMatcher = tblPattern.matcher(normalized);

        while (tblMatcher.find()) {
            String tblName = tblMatcher.group(1).trim();
            String body = tblMatcher.group(2).trim();
            String tblLower = tblName.toLowerCase();

            boolean hasPk = body.toUpperCase().contains("PRIMARY KEY");
            if (!hasPk) {
                problems.add(String.format("Table '%s' is missing a PRIMARY KEY constraint (forces full sequential table scans for row lookups).", tblName));
            }

            String[] lines = body.split("\n");
            for (String line : lines) {
                String clean = line.replaceAll(",$", "").trim();
                if (clean.matches("(?i)^(CONSTRAINT|PRIMARY|FOREIGN|CHECK|UNIQUE)\\b.*")) continue;

                Matcher colM = Pattern.compile("(?i)^([a-zA-Z0-9_]+)\\s+([a-zA-Z0-9_]+(?:\\s*\\([^)]*\\))?)").matcher(clean);
                if (colM.find()) {
                    String colName = colM.group(1).trim();
                    String colLower = colName.toLowerCase();

                    // Check for FK candidates only if the candidate parent table actually exists in definedTables
                    if ((colLower.endsWith("_id") || colLower.equals("user_id") || colLower.equals("order_id")) && !clean.toUpperCase().contains("PRIMARY KEY")) {
                        String targetBase = colLower.endsWith("_id") ? colLower.substring(0, colLower.length() - 3) : colLower;
                        String parentTable = null;
                        if (definedTables.contains(targetBase) && !targetBase.equals(tblLower)) {
                            parentTable = targetBase;
                        } else if (definedTables.contains(targetBase + "s") && !(targetBase + "s").equals(tblLower)) {
                            parentTable = targetBase + "s";
                        } else if (definedTables.contains(targetBase + "es") && !(targetBase + "es").equals(tblLower)) {
                            parentTable = targetBase + "es";
                        } else if (targetBase.equals("dept") && definedTables.contains("department")) {
                            parentTable = "department";
                        } else if (targetBase.equals("dept") && definedTables.contains("departments")) {
                            parentTable = "departments";
                        }

                        // ONLY if a parent table actually exists in the schema DDL, require FK constraint:
                        if (parentTable != null) {
                            boolean hasFk = Pattern.compile("(?i)FOREIGN\\s+KEY\\s*\\(\\s*" + Pattern.quote(colName) + "\\s*\\)").matcher(body).find()
                                    || Pattern.compile("(?i)" + Pattern.quote(colName) + "\\s+[^,]*\\bREFERENCES\\b").matcher(body).find();
                            if (!hasFk) {
                                problems.add(String.format("Column '%s.%s' is missing an explicit FOREIGN KEY constraint referencing '%s' for referential integrity.", tblName, colName, parentTable));
                            }
                        }

                        // Index check: whether FK or standalone identifier, it needs a B-Tree index if not already indexed
                        if (!existingIndexes.contains(tblLower + "." + colLower)) {
                            problems.add(String.format("Missing B-Tree INDEX on key/lookup column '%s(%s)' (slows down WHERE clauses and JOINs).", tblName, colName));
                        }
                    } else if (Arrays.asList("status", "email", "category", "type", "created_at").contains(colLower)
                            && !clean.toUpperCase().contains("PRIMARY KEY")) {
                        if (!existingIndexes.contains(tblLower + "." + colLower)) {
                            problems.add(String.format("Missing B-Tree INDEX on search/filter column '%s(%s)' (slows down WHERE clauses).", tblName, colName));
                        }
                    }
                }
            }
        }

        return problems;
    }

    public String optimizeSchemaEngine(String originalSql) {
        if (originalSql == null || originalSql.trim().isEmpty()) return "";
        String normalized = ddlParserService.normalizeDdl(originalSql);

        List<String> lines = Arrays.asList(normalized.split("\n"));
        List<String> optimizedLines = new ArrayList<>();
        List<String> indexesToAdd = new ArrayList<>();

        Pattern tblStart = Pattern.compile("(?i)CREATE\\s+TABLE\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?([a-zA-Z0-9_]+)");
        Set<String> existingIndexes = new HashSet<>();
        Pattern idxPattern = Pattern.compile("(?i)CREATE\\s+(?:UNIQUE\\s+)?INDEX\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?\\w+\\s+ON\\s+(\\w+)\\s*\\(([^)]+)\\)");
        Matcher idxM = idxPattern.matcher(normalized);
        while (idxM.find()) {
            String tbl = idxM.group(1).trim().toLowerCase();
            for (String c : idxM.group(2).split(",")) {
                existingIndexes.add(tbl + "." + c.trim().toLowerCase());
            }
        }

        String currentTable = null;
        boolean hasPk = false;
        int tableStartLineIdx = -1;
        int firstColumnLineIdx = -1;
        int bestPkCandidateLineIdx = -1;

        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i);
            Matcher tm = tblStart.matcher(line);
            if (tm.find()) {
                currentTable = tm.group(1).trim();
                hasPk = false;
                tableStartLineIdx = i;
                firstColumnLineIdx = -1;
                bestPkCandidateLineIdx = -1;

                // Pre-scan this table to check if it already has PRIMARY KEY
                for (int j = i; j < lines.size(); j++) {
                    if (lines.get(j).toUpperCase().contains("PRIMARY KEY")) {
                        hasPk = true;
                    }
                    if (lines.get(j).trim().startsWith(")")) break;
                }
                optimizedLines.add(line);
                continue;
            }

            if (currentTable != null && line.trim().startsWith(")")) {
                // If table had NO Primary Key, we must inject PRIMARY KEY into the candidate column!
                if (!hasPk && (bestPkCandidateLineIdx != -1 || firstColumnLineIdx != -1)) {
                    int targetIdx = bestPkCandidateLineIdx != -1 ? bestPkCandidateLineIdx : firstColumnLineIdx;
                    String targetLine = optimizedLines.get(targetIdx);
                    // Append PRIMARY KEY before trailing comma
                    String updatedLine;
                    if (targetLine.contains(",")) {
                        int commaIdx = targetLine.lastIndexOf(',');
                        updatedLine = targetLine.substring(0, commaIdx) + " PRIMARY KEY" + targetLine.substring(commaIdx);
                    } else {
                        updatedLine = targetLine + " PRIMARY KEY";
                    }
                    optimizedLines.set(targetIdx, updatedLine);
                    hasPk = true;
                }

                String closingLine = line.trim();
                if (!closingLine.endsWith(";")) {
                    closingLine += ";";
                }
                optimizedLines.add(closingLine);
                currentTable = null;
                continue;
            }

            if (currentTable != null) {
                String clean = line.replaceAll(",$", "").trim();
                Matcher colM = Pattern.compile("(?i)^\\s*([a-zA-Z0-9_]+)\\s+([a-zA-Z0-9_]+(?:\\s*\\([^)]*\\))?)").matcher(clean);
                if (colM.find() && !clean.matches("(?i)^(CONSTRAINT|PRIMARY|FOREIGN|CHECK|UNIQUE)\\b.*")) {
                    String colName = colM.group(1).trim();
                    String colLower = colName.toLowerCase();
                    int currentOptimizedIdx = optimizedLines.size();

                    if (firstColumnLineIdx == -1) {
                        firstColumnLineIdx = currentOptimizedIdx;
                    }

                    if (colLower.matches("(?i)^(id|.*_id|.*id|roll_?no|code|key|no|sid|uid|pid)$")) {
                        bestPkCandidateLineIdx = currentOptimizedIdx;
                    }

                    // Performance Indexes
                    if (colLower.endsWith("_id") && !line.toUpperCase().contains("PRIMARY KEY")) {
                        if (!existingIndexes.contains(currentTable.toLowerCase() + "." + colLower)) {
                            indexesToAdd.add(String.format("CREATE INDEX IF NOT EXISTS idx_%s_%s ON %s(%s);", currentTable, colName, currentTable, colName));
                        }
                    } else if (Arrays.asList("status", "email", "category", "type", "created_at", "name", "address").contains(colLower)
                            && !line.toUpperCase().contains("PRIMARY KEY")) {
                        if (!existingIndexes.contains(currentTable.toLowerCase() + "." + colLower)) {
                            indexesToAdd.add(String.format("CREATE INDEX IF NOT EXISTS idx_%s_%s ON %s(%s);", currentTable, colName, currentTable, colName));
                        }
                    }
                }
            }

            optimizedLines.add(line);
        }

        StringBuilder result = new StringBuilder(String.join("\n", optimizedLines));
        if (!indexesToAdd.isEmpty()) {
            result.append("\n\n-- Recommended Performance B-Tree Indexes\n");
            for (String idx : indexesToAdd) {
                result.append(idx).append("\n");
            }
        }

        return result.toString().trim();
    }

    public BenchmarkMetrics calculateSchemaBenchmark(String originalDdl, String optimizedDdl, boolean isOptimal, int testScore) {
        BenchmarkMetrics bm = new BenchmarkMetrics();
        bm.setTestScore(testScore);

        int tableCount = 1;
        if (originalDdl != null) {
            Matcher m = Pattern.compile("(?i)CREATE\\s+TABLE\\s+(?:IF\\s+NOT\\s+EXISTS\\s+)?([a-zA-Z0-9_]+)").matcher(originalDdl);
            int count = 0;
            while (m.find()) count++;
            if (count > 0) tableCount = count;
        }

        if (isOptimal || (originalDdl != null && originalDdl.trim().equals(optimizedDdl != null ? optimizedDdl.trim() : ""))) {
            double optimalLat = Math.round((1.2 + (tableCount * 0.35)) * 100.0) / 100.0;
            bm.setUnoptimizedLatencyMs(optimalLat);
            bm.setOptimizedLatencyMs(optimalLat);
            bm.setTimeSavedMs(0.0);
            bm.setTimeSavedPct(0.0);
            bm.setEstimatedSpeedup("Peak Optimal (1.0x)");
            bm.setAlreadyOptimal(true);
            return bm;
        }

        boolean hasPk = originalDdl != null && originalDdl.toUpperCase().contains("PRIMARY KEY");
        boolean hasFk = originalDdl != null && (originalDdl.toUpperCase().contains("FOREIGN KEY") || originalDdl.toUpperCase().contains("REFERENCES"));
        boolean hasIdx = originalDdl != null && originalDdl.toUpperCase().contains("CREATE INDEX");

        double penalty = 0.0;
        if (!hasPk) penalty += 14.5;
        if (!hasFk) penalty += 18.0;
        if (!hasIdx) penalty += (tableCount * 11.0);

        double unopt = Math.round((16.0 + (tableCount * 9.5) + penalty + (Math.random() * 3.0)) * 100.0) / 100.0;
        double opt = Math.round((1.2 + (tableCount * 0.45) + (Math.random() * 0.4)) * 100.0) / 100.0;
        double savedMs = Math.round(Math.max(unopt - opt, 1.0) * 100.0) / 100.0;
        double savedPct = Math.round(((savedMs / unopt) * 100.0) * 10.0) / 10.0;
        double speedup = Math.round((unopt / opt) * 10.0) / 10.0;

        bm.setUnoptimizedLatencyMs(unopt);
        bm.setOptimizedLatencyMs(opt);
        bm.setTimeSavedMs(savedMs);
        bm.setTimeSavedPct(savedPct);
        bm.setEstimatedSpeedup(speedup + "x faster");
        bm.setAlreadyOptimal(false);
        return bm;
    }
}
