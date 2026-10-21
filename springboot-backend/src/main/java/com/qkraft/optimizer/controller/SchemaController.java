package com.qkraft.optimizer.controller;

import com.qkraft.optimizer.dto.AnalyzeDtos.*;
import com.qkraft.optimizer.dto.DiagramDtos.*;
import com.qkraft.optimizer.dto.SchemaCreateRequest;
import com.qkraft.optimizer.model.QueryHistoryRecord;
import com.qkraft.optimizer.model.SchemaRecord;
import com.qkraft.optimizer.repository.QueryHistoryRepository;
import com.qkraft.optimizer.repository.SchemaRepository;
import com.qkraft.optimizer.service.DdlParserService;
import com.qkraft.optimizer.service.SandboxExecutionService;
import com.qkraft.optimizer.service.SchemaOptimizerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@CrossOrigin(origins = "*")
public class SchemaController {

    @Autowired
    private SchemaRepository schemaRepository;

    @Autowired
    private QueryHistoryRepository queryHistoryRepository;

    @Autowired
    private DdlParserService ddlParserService;

    @Autowired
    private SchemaOptimizerService schemaOptimizerService;

    @Autowired
    private SandboxExecutionService sandboxExecutionService;

    @GetMapping("/api/health")
    public Map<String, String> health() {
        return Map.of(
            "message", "Welcome to QKraft API - Spring Boot AI Schema & Query Optimizer",
            "database", "PostgreSQL",
            "status", "UP"
        );
    }

    @DeleteMapping("/api/schema/{id}")
    public ResponseEntity<?> deleteSchema(@PathVariable("id") Long id) {
        if (schemaRepository.existsById(id)) {
            queryHistoryRepository.deleteAll(queryHistoryRepository.findAllBySchemaIdOrderByIdDesc(id));
            schemaRepository.deleteById(id);
            return ResponseEntity.ok(Map.of("status", "success", "message", "Schema deleted"));
        }
        return ResponseEntity.notFound().build();
    }

    @GetMapping({"/api/schemas", "/api/schema"})
    public List<SchemaRecord> getAllSchemas() {
        return schemaRepository.findAllByOrderByIdDesc();
    }

    @GetMapping("/api/schema/{id}")
    public ResponseEntity<SchemaRecord> getSchemaById(@PathVariable("id") Long id) {
        return schemaRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/api/schema")
    public SchemaRecord createSchema(@RequestBody SchemaCreateRequest request) {
        SchemaRecord rec = new SchemaRecord(
                request.getName(),
                request.getContent(),
                request.getOptimizedContent(),
                request.getDiagramData()
        );
        return schemaRepository.save(rec);
    }

    @PostMapping("/api/schema/analyze")
    public AnalyzeResponse analyzeSchema(@RequestBody AnalyzeRequest request) {
        String content = request.getSchemaContent() != null ? request.getSchemaContent().trim() : "";
        AnalyzeResponse resp = new AnalyzeResponse();

        if (content.isEmpty()) {
            resp.setRecommendations(List.of());
            resp.setOptimal(true);
            resp.setScore(100);
            resp.setDetectedIssuesCount(0);
            return resp;
        }

        List<String> problems = schemaOptimizerService.detectSchemaProblems(content);
        if (problems.isEmpty()) {
            resp.setRecommendations(List.of());
            resp.setOptimal(true);
            resp.setScore(100);
            resp.setDetectedIssuesCount(0);
        } else {
            resp.setRecommendations(problems);
            resp.setOptimal(false);
            resp.setScore(Math.max(100 - (problems.size() * 18), 15));
            resp.setDetectedIssuesCount(problems.size());
        }
        return resp;
    }

    @PostMapping("/api/schema/recommend")
    public RecommendResponse recommendSchema(@RequestBody Map<String, Object> payload) {
        String content = (String) payload.getOrDefault("schema_content", "");
        if (content == null || content.trim().isEmpty()) {
            content = (String) payload.getOrDefault("ddl", "");
        }

        List<String> problems = schemaOptimizerService.detectSchemaProblems(content);
        String optimizedDdl = schemaOptimizerService.optimizeSchemaEngine(content);

        // Normalize both original and optimized to compare if structural changes were introduced
        String normOrig = content.replaceAll("(?m)^\\s*--.*$", "").replaceAll("\\s+", " ").trim();
        String normOpt = optimizedDdl.replaceAll("(?m)^\\s*--.*$", "").replaceAll("\\s+", " ").trim();
        boolean noStructuralChanges = normOrig.equalsIgnoreCase(normOpt);

        boolean isOptimal = problems.isEmpty() || noStructuralChanges;
        if (noStructuralChanges) {
            problems.clear();
        }
        int score = isOptimal ? 100 : Math.max(100 - (problems.size() * 18), 15);

        BenchmarkMetrics benchmark = schemaOptimizerService.calculateSchemaBenchmark(content, optimizedDdl, isOptimal, score);

        RecommendResponse resp = new RecommendResponse();
        resp.setStatus("success");
        resp.setRecommendedSchema(optimizedDdl);
        resp.setBenchmark(benchmark);
        resp.setAlreadyOptimal(isOptimal);
        resp.setTestScore(score);
        resp.setDetectedIssuesCount(problems.size());
        resp.setMessage(isOptimal ? "Schema already meets top database design practices!" : "Optimizations applied: added primary keys, foreign keys, and B-Tree indexes.");
        return resp;
    }

    @PostMapping("/api/schema/execute")
    public ResponseEntity<?> executeSchema(@RequestBody SchemaExecuteRequest request) {
        try {
            Long schemaId = request.getSchemaId();
            String ddl = request.getSchemaContent() != null ? request.getSchemaContent() : request.getDdl();

            if (schemaId == null || schemaId <= 0) {
                // Save schema first if not provided
                SchemaRecord newRec = new SchemaRecord(
                        request.getSchemaName() != null ? request.getSchemaName() : "Database Schema",
                        ddl,
                        ddl,
                        null
                );
                newRec = schemaRepository.save(newRec);
                schemaId = newRec.getId();
            }

            SchemaExecuteResponse resp = sandboxExecutionService.executeAndPopulateSandbox(schemaId, ddl);
            return ResponseEntity.ok(resp);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().body(Map.of("status", "error", "message", e.getMessage()));
        }
    }

    @GetMapping("/api/schema/{schemaId}/history")
    public List<QueryHistoryRecord> getSchemaHistory(@PathVariable("schemaId") Long schemaId) {
        return queryHistoryRepository.findAllBySchemaIdOrderByIdDesc(schemaId);
    }
}
