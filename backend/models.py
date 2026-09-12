from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class SchemaRecord(Base):
    __tablename__ = "schemas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, default="Untitled Schema")
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
