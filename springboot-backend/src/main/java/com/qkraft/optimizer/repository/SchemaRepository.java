package com.qkraft.optimizer.repository;

import com.qkraft.optimizer.model.SchemaRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SchemaRepository extends JpaRepository<SchemaRecord, Long> {
    List<SchemaRecord> findAllByOrderByIdDesc();
}
