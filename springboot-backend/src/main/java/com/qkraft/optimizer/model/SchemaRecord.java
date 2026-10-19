package com.qkraft.optimizer.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "schemas")
public class SchemaRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name")
    private String name = "Untitled Schema";

    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Column(name = "optimized_content", columnDefinition = "TEXT")
    @JsonProperty("optimized_content")
    private String optimizedContent;

    @Column(name = "diagram_data", columnDefinition = "TEXT")
    @JsonProperty("diagram_data")
    private String diagramData;

    @Column(name = "executed")
    private Boolean executed = false;

    @Column(name = "created_at")
    @JsonProperty("created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    public SchemaRecord() {}

    public SchemaRecord(String name, String content, String optimizedContent, String diagramData) {
        this.name = name != null && !name.trim().isEmpty() ? name : "Untitled Schema";
        this.content = content;
        this.optimizedContent = optimizedContent;
        this.diagramData = diagramData;
        this.createdAt = LocalDateTime.now();
        this.executed = false;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getOptimizedContent() { return optimizedContent; }
    public void setOptimizedContent(String optimizedContent) { this.optimizedContent = optimizedContent; }

    public String getDiagramData() { return diagramData; }
    public void setDiagramData(String diagramData) { this.diagramData = diagramData; }

    public Boolean getExecuted() { return executed; }
    public void setExecuted(Boolean executed) { this.executed = executed; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
