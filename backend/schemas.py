from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SchemaBase(BaseModel):
    name: str = "Untitled Schema"
    content: str

class SchemaCreate(SchemaBase):
    pass

class SchemaResponse(SchemaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    query: str
    schema_content: str

class QueryResponse(BaseModel):
    status: str
    optimized_sql: str

class AnalyzeRequest(BaseModel):
    schema_content: str

class AnalyzeResponse(BaseModel):
    status: str
    recommendations: List[str]
