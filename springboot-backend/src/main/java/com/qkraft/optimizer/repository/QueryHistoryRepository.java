package com.qkraft.optimizer.repository;

import com.qkraft.optimizer.model.QueryHistoryRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface QueryHistoryRepository extends JpaRepository<QueryHistoryRecord, Long> {
    List<QueryHistoryRecord> findAllBySchemaIdOrderByIdDesc(Long schemaId);
}
