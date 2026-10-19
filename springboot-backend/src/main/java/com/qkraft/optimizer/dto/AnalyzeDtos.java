package com.qkraft.optimizer.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class AnalyzeDtos {

    public static class AnalyzeRequest {
        @JsonProperty("schema_content")
        private String schemaContent;

        public String getSchemaContent() { return schemaContent; }
        public void setSchemaContent(String schemaContent) { this.schemaContent = schemaContent; }
    }

    public static class AnalyzeResponse {
        private String status = "success";
        private List<String> recommendations;

        @JsonProperty("is_optimal")
        private boolean isOptimal = false;

        private int score = 100;

        @JsonProperty("detected_issues_count")
        private int detectedIssuesCount = 0;

        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }

        public List<String> getRecommendations() { return recommendations; }
        public void setRecommendations(List<String> recommendations) { this.recommendations = recommendations; }

        public boolean isOptimal() { return isOptimal; }
        public void setOptimal(boolean optimal) { isOptimal = optimal; }

        public int getScore() { return score; }
        public void setScore(int score) { this.score = score; }

        public int getDetectedIssuesCount() { return detectedIssuesCount; }
        public void setDetectedIssuesCount(int detectedIssuesCount) { this.detectedIssuesCount = detectedIssuesCount; }
    }

    public static class BenchmarkMetrics {
        @JsonProperty("unoptimized_latency_ms")
        private double unoptimizedLatencyMs;

        @JsonProperty("optimized_latency_ms")
        private double optimizedLatencyMs;

        @JsonProperty("time_saved_ms")
        private double timeSavedMs;

        @JsonProperty("time_saved_pct")
        private double timeSavedPct;

        @JsonProperty("estimated_speedup")
        private String estimatedSpeedup;

        @JsonProperty("test_score")
        private int testScore = 100;

        @JsonProperty("is_already_optimal")
        private boolean isAlreadyOptimal = false;

        public double getUnoptimizedLatencyMs() { return unoptimizedLatencyMs; }
        public void setUnoptimizedLatencyMs(double unoptimizedLatencyMs) { this.unoptimizedLatencyMs = unoptimizedLatencyMs; }

        public double getOptimizedLatencyMs() { return optimizedLatencyMs; }
        public void setOptimizedLatencyMs(double optimizedLatencyMs) { this.optimizedLatencyMs = optimizedLatencyMs; }

        public double getTimeSavedMs() { return timeSavedMs; }
        public void setTimeSavedMs(double timeSavedMs) { this.timeSavedMs = timeSavedMs; }

        public double getTimeSavedPct() { return timeSavedPct; }
        public void setTimeSavedPct(double timeSavedPct) { this.timeSavedPct = timeSavedPct; }

        public String getEstimatedSpeedup() { return estimatedSpeedup; }
        public void setEstimatedSpeedup(String estimatedSpeedup) { this.estimatedSpeedup = estimatedSpeedup; }

        public int getTestScore() { return testScore; }
        public void setTestScore(int testScore) { this.testScore = testScore; }

        public boolean isAlreadyOptimal() { return isAlreadyOptimal; }
        public void setAlreadyOptimal(boolean alreadyOptimal) { isAlreadyOptimal = alreadyOptimal; }
    }

    public static class RecommendResponse {
        private String status = "success";

        @JsonProperty("recommended_schema")
        private String recommendedSchema;

        private BenchmarkMetrics benchmark;

        @JsonProperty("is_already_optimal")
        private boolean isAlreadyOptimal = false;

        @JsonProperty("test_score")
        private int testScore = 100;

        @JsonProperty("detected_issues_count")
        private int detectedIssuesCount = 0;

        private String message;

        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }

        public String getRecommendedSchema() { return recommendedSchema; }
        public void setRecommendedSchema(String recommendedSchema) { this.recommendedSchema = recommendedSchema; }

        public BenchmarkMetrics getBenchmark() { return benchmark; }
        public void setBenchmark(BenchmarkMetrics benchmark) { this.benchmark = benchmark; }

        public boolean isAlreadyOptimal() { return isAlreadyOptimal; }
        public void setAlreadyOptimal(boolean alreadyOptimal) { isAlreadyOptimal = alreadyOptimal; }

        public int getTestScore() { return testScore; }
        public void setTestScore(int testScore) { this.testScore = testScore; }

        public int getDetectedIssuesCount() { return detectedIssuesCount; }
        public void setDetectedIssuesCount(int detectedIssuesCount) { this.detectedIssuesCount = detectedIssuesCount; }

        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
    }
}
