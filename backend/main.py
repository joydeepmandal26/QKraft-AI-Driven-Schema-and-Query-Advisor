from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="QKraft API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to QKraft API"}

@app.post("/api/schema", response_model=schemas.SchemaResponse)
def create_schema(schema: schemas.SchemaCreate, db: Session = Depends(get_db)):
    db_schema = models.SchemaRecord(name=schema.name, content=schema.content)
    db.add(db_schema)
    db.commit()
    db.refresh(db_schema)
    return db_schema

@app.post("/api/advisor/chat", response_model=schemas.QueryResponse)
def advisor_chat(payload: schemas.QueryRequest):
    # TODO: Integrate AI model properly
    # For now, return a mocked optimized SQL
    return {"status": "success", "optimized_sql": f"SELECT * FROM simulated_table WHERE query='{payload.query}'"}

@app.post("/api/schema/analyze", response_model=schemas.AnalyzeResponse)
def analyze_schema(payload: schemas.AnalyzeRequest):
    # TODO: Implement performance rating logic based on payload.schema_content
    return {"status": "success", "recommendations": ["Add index on user_id", "Consider foreign key on orders.user_id"]}

