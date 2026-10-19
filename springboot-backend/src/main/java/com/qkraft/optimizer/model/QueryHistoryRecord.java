package com.qkraft.optimizer.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "query_histories")
public class QueryHistoryRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "schema_id")
    @JsonProperty("schema_id")
    private Long schemaId;

    @Column(name = "user_prompt", columnDefinition = "TEXT")
    @JsonProperty("user_prompt")
    private String userPrompt;

    @Column(name = "optimized_sql", columnDefinition = "TEXT")
    @JsonProperty("optimized_sql")
    private String optimizedSql;

    @Column(name = "unoptimized_sql", columnDefinition = "TEXT")
    @JsonProperty("unoptimized_sql")
    private String unoptimizedSql;

    @Column(name = "optimized_time_ms")
    @JsonProperty("optimized_time_ms")
    private Double optimizedTimeMs = 0.0;

    @Column(name = "unoptimized_time_ms")
    @JsonProperty("unoptimized_time_ms")
    private Double unoptimizedTimeMs = 0.0;

    @Column(name = "time_saved_ms")
    @JsonProperty("time_saved_ms")
    private Double timeSavedMs = 0.0;

    @Column(name = "time_saved_pct")
    @JsonProperty("time_saved_pct")
    private Double timeSavedPct = 0.0;

    @Column(name = "status")
    private String status = "SUCCESS";

    @Column(name = "execution_result", columnDefinition = "TEXT")
    @JsonProperty("execution_result")
    private String executionResult;

    @Column(name = "created_at")
    @JsonProperty("created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    public QueryHistoryRecord() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSchemaId() { return schemaId; }
    public void setSchemaId(Long schemaId) { this.schemaId = schemaId; }

    public String getUserPrompt() { return userPrompt; }
    public void setUserPrompt(String userPrompt) { this.userPrompt = userPrompt; }

    public String getOptimizedSql() { return optimizedSql; }
    public void setOptimizedSql(String optimizedSql) { this.optimizedSql = optimizedSql; }

    public String getUnoptimizedSql() { return unoptimizedSql; }
    public void setUnoptimizedSql(String unoptimizedSql) { this.unoptimizedSql = unoptimizedSql; }

    public Double getOptimizedTimeMs() { return optimizedTimeMs; }
    public void setOptimizedTimeMs(Double optimizedTimeMs) { this.optimizedTimeMs = optimizedTimeMs; }

    public Double getUnoptimizedTimeMs() { return unoptimizedTimeMs; }
    public void setUnoptimizedTimeMs(Double unoptimizedTimeMs) { this.unoptimizedTimeMs = unoptimizedTimeMs; }

    public Double getTimeSavedMs() { return timeSavedMs; }
    public void setTimeSavedMs(Double timeSavedMs) { this.timeSavedMs = timeSavedMs; }

    public Double getTimeSavedPct() { return timeSavedPct; }
    public void setTimeSavedPct(Double timeSavedPct) { this.timeSavedPct = timeSavedPct; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getExecutionResult() { return executionResult; }
    public void setExecutionResult(String executionResult) { this.executionResult = executionResult; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
