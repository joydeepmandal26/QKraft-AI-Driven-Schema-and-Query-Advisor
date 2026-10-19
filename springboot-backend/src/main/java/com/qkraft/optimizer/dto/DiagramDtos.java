package com.qkraft.optimizer.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class DiagramDtos {

    public static class ColumnInfo {
        private String name;
        private String type;

        @JsonProperty("is_pk")
        private boolean isPk = false;

        @JsonProperty("is_fk")
        private boolean isFk = false;

        private String references;

        @JsonProperty("is_indexed")
        private boolean isIndexed = false;

        public ColumnInfo() {}

        public ColumnInfo(String name, String type, boolean isPk, boolean isFk, String references, boolean isIndexed) {
            this.name = name;
            this.type = type;
            this.isPk = isPk;
            this.isFk = isFk;
            this.references = references;
            this.isIndexed = isIndexed;
        }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }

        public String getType() { return type; }
        public void setType(String type) { this.type = type; }

        public boolean isPk() { return isPk; }
        public void setPk(boolean pk) { isPk = pk; }

        public boolean isFk() { return isFk; }
        public void setFk(boolean fk) { isFk = fk; }

        public String getReferences() { return references; }
        public void setReferences(String references) { this.references = references; }

        public boolean isIndexed() { return isIndexed; }
        public void setIndexed(boolean indexed) { isIndexed = indexed; }
    }

    public static class TableInfo {
        private String name;
        private List<ColumnInfo> columns = new ArrayList<>();

        @JsonProperty("row_count")
        private int rowCount = 0;

        public TableInfo() {}

        public TableInfo(String name, List<ColumnInfo> columns, int rowCount) {
            this.name = name;
            this.columns = columns;
            this.rowCount = rowCount;
        }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }

        public List<ColumnInfo> getColumns() { return columns; }
        public void setColumns(List<ColumnInfo> columns) { this.columns = columns; }

        public int getRowCount() { return rowCount; }
        public void setRowCount(int rowCount) { this.rowCount = rowCount; }
    }

    public static class RelationInfo {
        @JsonProperty("from_table")
        private String fromTable;

        @JsonProperty("from_column")
        private String fromColumn;

        @JsonProperty("to_table")
        private String toTable;

        @JsonProperty("to_column")
        private String toColumn;

        public RelationInfo() {}

        public RelationInfo(String fromTable, String fromColumn, String toTable, String toColumn) {
            this.fromTable = fromTable;
            this.fromColumn = fromColumn;
            this.toTable = toTable;
            this.toColumn = toColumn;
        }

        public String getFromTable() { return fromTable; }
        public void setFromTable(String fromTable) { this.fromTable = fromTable; }

        public String getFromColumn() { return fromColumn; }
        public void setFromColumn(String fromColumn) { this.fromColumn = fromColumn; }

        public String getToTable() { return toTable; }
        public void setToTable(String toTable) { this.toTable = toTable; }

        public String getToColumn() { return toColumn; }
        public void setToColumn(String toColumn) { this.toColumn = toColumn; }
    }

    public static class DiagramData {
        private List<TableInfo> tables = new ArrayList<>();
        private List<RelationInfo> relations = new ArrayList<>();

        public DiagramData() {}

        public DiagramData(List<TableInfo> tables, List<RelationInfo> relations) {
            this.tables = tables;
            this.relations = relations;
        }

        public List<TableInfo> getTables() { return tables; }
        public void setTables(List<TableInfo> tables) { this.tables = tables; }

        public List<RelationInfo> getRelations() { return relations; }
        public void setRelations(List<RelationInfo> relations) { this.relations = relations; }
    }

    public static class SchemaExecuteRequest {
        @JsonProperty("schema_id")
        private Long schemaId;

        @JsonProperty("schema_content")
        private String schemaContent;

        private String ddl;

        @JsonProperty("schema_name")
        private String schemaName = "Database Schema";

        public Long getSchemaId() { return schemaId; }
        public void setSchemaId(Long schemaId) { this.schemaId = schemaId; }

        public String getSchemaContent() { return schemaContent; }
        public void setSchemaContent(String schemaContent) { this.schemaContent = schemaContent; }

        public String getDdl() { return ddl; }
        public void setDdl(String ddl) { this.ddl = ddl; }

        public String getSchemaName() { return schemaName; }
        public void setSchemaName(String schemaName) { this.schemaName = schemaName; }
    }

    public static class SchemaExecuteResponse {
        private String status = "success";

        @JsonProperty("schema_id")
        private Long schemaId;

        private String message;
        private DiagramData diagram;

        @JsonProperty("tables_created")
        private List<String> tablesCreated = new ArrayList<>();

        @JsonProperty("sample_records_count")
        private int sampleRecordsCount = 0;

        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }

        public Long getSchemaId() { return schemaId; }
        public void setSchemaId(Long schemaId) { this.schemaId = schemaId; }

        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }

        public DiagramData getDiagram() { return diagram; }
        public void setDiagram(DiagramData diagram) { this.diagram = diagram; }

        public List<String> getTablesCreated() { return tablesCreated; }
        public void setTablesCreated(List<String> tablesCreated) { this.tablesCreated = tablesCreated; }

        public int getSampleRecordsCount() { return sampleRecordsCount; }
        public void setSampleRecordsCount(int sampleRecordsCount) { this.sampleRecordsCount = sampleRecordsCount; }
    }
}
