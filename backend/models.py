from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class SchemaRecord(Base):
    __tablename__ = "schemas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, default="Untitled Schema")
    content = Column(Text)
    optimized_content = Column(Text, nullable=True)
    diagram_data = Column(Text, nullable=True)  # JSON string of nodes, columns, relationships
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    query_histories = relationship("QueryHistoryRecord", back_populates="schema_rel", cascade="all, delete-orphan")

class QueryHistoryRecord(Base):
    __tablename__ = "query_histories"

    id = Column(Integer, primary_key=True, index=True)
    schema_id = Column(Integer, ForeignKey("schemas.id", ondelete="CASCADE"), index=True)
    user_prompt = Column(Text)
    optimized_sql = Column(Text)
    unoptimized_sql = Column(Text, nullable=True)
    unoptimized_time_ms = Column(Float, default=0.0)
    optimized_time_ms = Column(Float, default=0.0)
    time_saved_pct = Column(Float, default=0.0)
    time_saved_ms = Column(Float, default=0.0)
    status = Column(String, default="SUCCESS")
    execution_result = Column(Text, nullable=True) # JSON summary of execution (row count, columns, sample)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    schema_rel = relationship("SchemaRecord", back_populates="query_histories")
