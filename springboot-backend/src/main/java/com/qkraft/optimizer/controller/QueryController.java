package com.qkraft.optimizer.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.qkraft.optimizer.dto.QueryDtos.*;
import com.qkraft.optimizer.model.QueryHistoryRecord;
import com.qkraft.optimizer.model.SchemaRecord;
import com.qkraft.optimizer.repository.QueryHistoryRepository;
import com.qkraft.optimizer.repository.SchemaRepository;
import com.qkraft.optimizer.service.QueryAdvisorService;
import com.qkraft.optimizer.service.SandboxExecutionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.util.Map;

@RestController
@CrossOrigin(origins = "*")
public class QueryController {

    @Autowired
    private QueryHistoryRepository queryHistoryRepository;

    @Autowired
    private SchemaRepository schemaRepository;

    @Autowired
    private SandboxExecutionService sandboxExecutionService;

    @Autowired
    private QueryAdvisorService queryAdvisorService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @PostMapping("/api/query/execute")
    public ResponseEntity<?> executeQuery(@RequestBody QueryExecuteRequest request) {
        Long schemaId = request.getSchemaId();
        String sql = request.getSqlQuery() != null ? request.getSqlQuery().trim() : "";

        if (sql.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("status", "error", "error", "SQL query is required"));
        }

        try {
            // Auto-initialize sandbox in PostgreSQL if not already created
            if (schemaId != null && !sandboxExecutionService.isSandboxInitialized(schemaId)) {
                schemaRepository.findById(schemaId).ifPresent(rec -> {
                    String ddl = rec.getOptimizedContent() != null ? rec.getOptimizedContent() : rec.getContent();
                    try {
                        sandboxExecutionService.executeAndPopulateSandbox(schemaId, ddl);
                    } catch (Exception ignored) {}
                });
            }

            QueryExecuteResponse resp = sandboxExecutionService.runQueryInSandbox(schemaId, sql, request.getUnoptimizedSql());

            // Save to query history
            QueryHistoryRecord history = new QueryHistoryRecord();
            history.setSchemaId(schemaId);
            history.setUserPrompt(request.getUserPrompt() != null ? request.getUserPrompt() : "SQL Execution");
            history.setOptimizedSql(sql);
            history.setUnoptimizedSql(request.getUnoptimizedSql());
            history.setOptimizedTimeMs(resp.getOptimizedTimeMs());
            history.setUnoptimizedTimeMs(resp.getUnoptimizedTimeMs());
            history.setTimeSavedMs(resp.getTimeSavedMs());
            history.setTimeSavedPct(resp.getTimeSavedPct());
            history.setStatus("SUCCESS");
            history.setExecutionResult(objectMapper.writeValueAsString(Map.of(
                    "row_count", resp.getRowCount(),
                    "columns", resp.getColumns()
            )));
            queryHistoryRepository.save(history);

            return ResponseEntity.ok(resp);
        } catch (Exception e) {
            e.printStackTrace();

            // Record error in query history
            try {
                QueryHistoryRecord history = new QueryHistoryRecord();
                history.setSchemaId(schemaId);
                history.setUserPrompt(request.getUserPrompt() != null ? request.getUserPrompt() : "SQL Execution");
                history.setOptimizedSql(sql);
                history.setUnoptimizedSql(request.getUnoptimizedSql());
                history.setStatus("ERROR");
                history.setExecutionResult(objectMapper.writeValueAsString(Map.of("error", e.getMessage())));
                queryHistoryRepository.save(history);
            } catch (Exception ignored) {}

            QueryExecuteResponse errResp = new QueryExecuteResponse();
            errResp.setStatus("error");
            errResp.setSchemaId(schemaId);
            errResp.setScanType("Failed");
            errResp.setError(e.getMessage());
            return ResponseEntity.ok(errResp);
        }
    }

    @PostMapping({"/api/advisor/chat", "/api/query/advisor"})
    public AdvisorQueryResponse getAdvisorChat(@RequestBody AdvisorQueryRequest request) {
        return queryAdvisorService.generateQueryAdvice(request);
    }
}
