package com.qkraft.optimizer.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class SchemaCreateRequest {
    private String name = "Untitled Schema";
    private String content;

    @JsonProperty("optimized_content")
    private String optimizedContent;

    @JsonProperty("diagram_data")
    private String diagramData;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getOptimizedContent() { return optimizedContent; }
    public void setOptimizedContent(String optimizedContent) { this.optimizedContent = optimizedContent; }

    public String getDiagramData() { return diagramData; }
    public void setDiagramData(String diagramData) { this.diagramData = diagramData; }
}
