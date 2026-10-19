from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class SchemaBase(BaseModel):
    name: str = "Untitled Schema"
    content: str

class SchemaCreate(SchemaBase):
    optimized_content: Optional[str] = None
    diagram_data: Optional[str] = None

class SchemaResponse(SchemaBase):
    id: int
    optimized_content: Optional[str] = None
    diagram_data: Optional[str] = None
    executed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

# Diagram Models
class ColumnInfo(BaseModel):
    name: str
    type: str
    is_pk: bool = False
    is_fk: bool = False
    references: Optional[str] = None
    is_indexed: bool = False

class TableInfo(BaseModel):
    name: str
    columns: List[ColumnInfo]
    row_count: int = 0

class RelationInfo(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str

class DiagramData(BaseModel):
    tables: List[TableInfo]
    relations: List[RelationInfo]

class SchemaExecuteRequest(BaseModel):
    schema_id: Optional[int] = None
    schema_content: Optional[str] = None
    ddl: Optional[str] = None
    schema_name: Optional[str] = "Database Schema"

class SchemaExecuteResponse(BaseModel):
    status: str
    schema_id: int
    message: str
    diagram: DiagramData
    tables_created: List[str]
    sample_records_count: int

# Query Advisor Models
class AdvisorQueryRequest(BaseModel):
    schema_id: Optional[int] = None
    query: str
    schema_content: Optional[str] = ""
    optimized_schema: Optional[str] = None

class OptimizationDetails(BaseModel):
    techniques_used: List[str]
    index_utilization: List[str]
    estimated_speedup: str
    rationale: str

class AdvisorQueryResponse(BaseModel):
    status: str
    optimized_sql: str
    unoptimized_sql: Optional[str] = None
    explanation: Optional[str] = None
    details: Optional[OptimizationDetails] = None

# Query Execution Models
class ExecutionStep(BaseModel):
    step_number: int
    name: str
    node_type: str # e.g. "AST Parse", "Cost Optimizer", "Index Scan", "Hash Join", "Materialize"
    duration_ms: float
    description: str
    status: str = "SUCCESS" # "SUCCESS", "OPTIMIZED", "WARNING"

class QueryExecuteRequest(BaseModel):
    schema_id: int
    sql_query: str
    unoptimized_sql: Optional[str] = None
    user_prompt: Optional[str] = None

class QueryExecuteResponse(BaseModel):
    status: str
    schema_id: int
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    optimized_time_ms: float
    unoptimized_time_ms: float
    time_saved_ms: float
    time_saved_pct: float
    scan_type: str
    execution_pipeline: List[ExecutionStep]
    explain_plan: List[str]
    error: Optional[str] = None

class QueryHistoryItem(BaseModel):
    id: int
    schema_id: int
    user_prompt: str
    optimized_sql: str
    unoptimized_sql: Optional[str] = None
    optimized_time_ms: float
    unoptimized_time_ms: float
    time_saved_ms: float
    time_saved_pct: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyzeRequest(BaseModel):
    schema_content: str

class AnalyzeResponse(BaseModel):
    status: str
    recommendations: List[str]
    is_optimal: bool = False
    score: int = 100
    detected_issues_count: int = 0

class BenchmarkMetrics(BaseModel):
    unoptimized_latency_ms: float
    optimized_latency_ms: float
    time_saved_ms: float
    time_saved_pct: float
    estimated_speedup: str
    test_score: int = 100
    is_already_optimal: bool = False

class RecommendResponse(BaseModel):
    status: str
    recommended_schema: str
    benchmark: Optional[BenchmarkMetrics] = None
    is_already_optimal: bool = False
    test_score: int = 100
    detected_issues_count: int = 0
    message: Optional[str] = None



