package com.qkraft.optimizer.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class QueryDtos {

    public static class OptimizationDetails {
        @JsonProperty("techniques_used")
        private List<String> techniquesUsed = new ArrayList<>();

        @JsonProperty("index_utilization")
        private List<String> indexUtilization = new ArrayList<>();

        @JsonProperty("estimated_speedup")
        private String estimatedSpeedup;

        private String rationale;

        public List<String> getTechniquesUsed() { return techniquesUsed; }
        public void setTechniquesUsed(List<String> techniquesUsed) { this.techniquesUsed = techniquesUsed; }

        public List<String> getIndexUtilization() { return indexUtilization; }
        public void setIndexUtilization(List<String> indexUtilization) { this.indexUtilization = indexUtilization; }

        public String getEstimatedSpeedup() { return estimatedSpeedup; }
        public void setEstimatedSpeedup(String estimatedSpeedup) { this.estimatedSpeedup = estimatedSpeedup; }

        public String getRationale() { return rationale; }
        public void setRationale(String rationale) { this.rationale = rationale; }
    }

    public static class AdvisorQueryRequest {
        @JsonProperty("schema_id")
        private Long schemaId;

        private String query;

        @JsonProperty("schema_content")
        private String schemaContent;

        @JsonProperty("optimized_schema")
        private String optimizedSchema;

        public Long getSchemaId() { return schemaId; }
        public void setSchemaId(Long schemaId) { this.schemaId = schemaId; }

        public String getQuery() { return query; }
        public void setQuery(String query) { this.query = query; }

        public String getSchemaContent() { return schemaContent; }
        public void setSchemaContent(String schemaContent) { this.schemaContent = schemaContent; }

        public String getOptimizedSchema() { return optimizedSchema; }
        public void setOptimizedSchema(String optimizedSchema) { this.optimizedSchema = optimizedSchema; }
    }

    public static class AdvisorQueryResponse {
        private String status = "success";

        @JsonProperty("optimized_sql")
        private String optimizedSql;

        @JsonProperty("unoptimized_sql")
        private String unoptimizedSql;

        private String explanation;
        private OptimizationDetails details;

        @JsonProperty("anti_patterns")
        private List<AntiPatternWarning> antiPatterns = new ArrayList<>();

        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }

        public String getOptimizedSql() { return optimizedSql; }
        public void setOptimizedSql(String optimizedSql) { this.optimizedSql = optimizedSql; }

        public String getUnoptimizedSql() { return unoptimizedSql; }
        public void setUnoptimizedSql(String unoptimizedSql) { this.unoptimizedSql = unoptimizedSql; }

        public String getExplanation() { return explanation; }
        public void setExplanation(String explanation) { this.explanation = explanation; }

        public OptimizationDetails getDetails() { return details; }
        public void setDetails(OptimizationDetails details) { this.details = details; }

        public List<AntiPatternWarning> getAntiPatterns() { return antiPatterns; }
        public void setAntiPatterns(List<AntiPatternWarning> antiPatterns) { this.antiPatterns = antiPatterns; }
    }

    public static class AntiPatternWarning {
        private String severity; // HIGH, MEDIUM, INFO
        private String pattern;
        private String description;
        private String suggestion;

        public AntiPatternWarning() {}

        public AntiPatternWarning(String severity, String pattern, String description, String suggestion) {
            this.severity = severity;
            this.pattern = pattern;
            this.description = description;
            this.suggestion = suggestion;
        }

        public String getSeverity() { return severity; }
        public void setSeverity(String severity) { this.severity = severity; }

        public String getPattern() { return pattern; }
        public void setPattern(String pattern) { this.pattern = pattern; }

        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }

        public String getSuggestion() { return suggestion; }
        public void setSuggestion(String suggestion) { this.suggestion = suggestion; }
    }

    public static class PlanNodeInfo {
        @JsonProperty("node_type")
        private String nodeType;

        @JsonProperty("relation_name")
        private String relationName;

        @JsonProperty("index_name")
        private String indexName;

        @JsonProperty("actual_time_ms")
        private double actualTimeMs;

        @JsonProperty("actual_rows")
        private int actualRows;

        @JsonProperty("cost_est")
        private String costEst;

        @JsonProperty("details")
        private String details;

        @JsonProperty("is_bottleneck")
        private boolean isBottleneck;

        public PlanNodeInfo() {}

        public PlanNodeInfo(String nodeType, String relationName, String indexName, double actualTimeMs, int actualRows, String costEst, String details, boolean isBottleneck) {
            this.nodeType = nodeType;
            this.relationName = relationName;
            this.indexName = indexName;
            this.actualTimeMs = actualTimeMs;
            this.actualRows = actualRows;
            this.costEst = costEst;
            this.details = details;
            this.isBottleneck = isBottleneck;
        }

        public String getNodeType() { return nodeType; }
        public void setNodeType(String nodeType) { this.nodeType = nodeType; }

        public String getRelationName() { return relationName; }
        public void setRelationName(String relationName) { this.relationName = relationName; }

        public String getIndexName() { return indexName; }
        public void setIndexName(String indexName) { this.indexName = indexName; }

        public double getActualTimeMs() { return actualTimeMs; }
        public void setActualTimeMs(double actualTimeMs) { this.actualTimeMs = actualTimeMs; }

        public int getActualRows() { return actualRows; }
        public void setActualRows(int actualRows) { this.actualRows = actualRows; }

        public String getCostEst() { return costEst; }
        public void setCostEst(String costEst) { this.costEst = costEst; }

        public String getDetails() { return details; }
        public void setDetails(String details) { this.details = details; }

        public boolean isBottleneck() { return isBottleneck; }
        public void setBottleneck(boolean bottleneck) { isBottleneck = bottleneck; }
    }

    public static class ExecutionStep {
        @JsonProperty("step_number")
        private int stepNumber;

        private String name;

        @JsonProperty("node_type")
        private String nodeType;

        @JsonProperty("duration_ms")
        private double durationMs;

        private String description;
        private String status = "SUCCESS";

        public ExecutionStep() {}

        public ExecutionStep(int stepNumber, String name, String nodeType, double durationMs, String description, String status) {
            this.stepNumber = stepNumber;
            this.name = name;
            this.nodeType = nodeType;
            this.durationMs = durationMs;
            this.description = description;
            this.status = status;
        }

        public int getStepNumber() { return stepNumber; }
        public void setStepNumber(int stepNumber) { this.stepNumber = stepNumber; }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }

        public String getNodeType() { return nodeType; }
        public void setNodeType(String nodeType) { this.nodeType = nodeType; }

        public double getDurationMs() { return durationMs; }
        public void setDurationMs(double durationMs) { this.durationMs = durationMs; }

        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }

        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
    }

    public static class QueryExecuteRequest {
        @JsonProperty("schema_id")
        private Long schemaId;

        @JsonProperty("sql_query")
        private String sqlQuery;

        @JsonProperty("unoptimized_sql")
        private String unoptimizedSql;

        @JsonProperty("user_prompt")
        private String userPrompt;

        @JsonProperty("schema_content")
        private String schemaContent;

        @JsonProperty("optimized_schema")
        private String optimizedSchema;

        public Long getSchemaId() { return schemaId; }
        public void setSchemaId(Long schemaId) { this.schemaId = schemaId; }

        public String getSqlQuery() { return sqlQuery; }
        public void setSqlQuery(String sqlQuery) { this.sqlQuery = sqlQuery; }

        public String getUnoptimizedSql() { return unoptimizedSql; }
        public void setUnoptimizedSql(String unoptimizedSql) { this.unoptimizedSql = unoptimizedSql; }

        public String getUserPrompt() { return userPrompt; }
        public void setUserPrompt(String userPrompt) { this.userPrompt = userPrompt; }

        public String getSchemaContent() { return schemaContent; }
        public void setSchemaContent(String schemaContent) { this.schemaContent = schemaContent; }

        public String getOptimizedSchema() { return optimizedSchema; }
        public void setOptimizedSchema(String optimizedSchema) { this.optimizedSchema = optimizedSchema; }
    }

    public static class QueryExecuteResponse {
        private String status = "success";

        @JsonProperty("schema_id")
        private Long schemaId;

        private List<String> columns = new ArrayList<>();
        private List<List<Object>> rows = new ArrayList<>();

        @JsonProperty("row_count")
        private int rowCount = 0;

        @JsonProperty("optimized_time_ms")
        private double optimizedTimeMs = 0.0;

        @JsonProperty("unoptimized_time_ms")
        private double unoptimizedTimeMs = 0.0;

        @JsonProperty("time_saved_ms")
        private double timeSavedMs = 0.0;

        @JsonProperty("time_saved_pct")
        private double timeSavedPct = 0.0;

        @JsonProperty("scan_type")
        private String scanType;

        @JsonProperty("execution_pipeline")
        private List<ExecutionStep> executionPipeline = new ArrayList<>();

        @JsonProperty("explain_plan")
        private List<String> explainPlan = new ArrayList<>();

        @JsonProperty("plan_nodes")
        private List<PlanNodeInfo> planNodes = new ArrayList<>();

        private String error;

        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }

        public Long getSchemaId() { return schemaId; }
        public void setSchemaId(Long schemaId) { this.schemaId = schemaId; }

        public List<String> getColumns() { return columns; }
        public void setColumns(List<String> columns) { this.columns = columns; }

        public List<List<Object>> getRows() { return rows; }
        public void setRows(List<List<Object>> rows) { this.rows = rows; }

        public int getRowCount() { return rowCount; }
        public void setRowCount(int rowCount) { this.rowCount = rowCount; }

        public double getOptimizedTimeMs() { return optimizedTimeMs; }
        public void setOptimizedTimeMs(double optimizedTimeMs) { this.optimizedTimeMs = optimizedTimeMs; }

        public double getUnoptimizedTimeMs() { return unoptimizedTimeMs; }
        public void setUnoptimizedTimeMs(double unoptimizedTimeMs) { this.unoptimizedTimeMs = unoptimizedTimeMs; }

        public double getTimeSavedMs() { return timeSavedMs; }
        public void setTimeSavedMs(double timeSavedMs) { this.timeSavedMs = timeSavedMs; }

        public double getTimeSavedPct() { return timeSavedPct; }
        public void setTimeSavedPct(double timeSavedPct) { this.timeSavedPct = timeSavedPct; }

        public String getScanType() { return scanType; }
        public void setScanType(String scanType) { this.scanType = scanType; }

        public List<ExecutionStep> getExecutionPipeline() { return executionPipeline; }
        public void setExecutionPipeline(List<ExecutionStep> executionPipeline) { this.executionPipeline = executionPipeline; }

        public List<String> getExplainPlan() { return explainPlan; }
        public void setExplainPlan(List<String> explainPlan) { this.explainPlan = explainPlan; }

        public List<PlanNodeInfo> getPlanNodes() { return planNodes; }
        public void setPlanNodes(List<PlanNodeInfo> planNodes) { this.planNodes = planNodes; }

        public String getError() { return error; }
        public void setError(String error) { this.error = error; }
    }
}
