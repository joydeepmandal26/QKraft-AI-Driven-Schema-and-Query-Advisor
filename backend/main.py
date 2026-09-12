from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"You are a Postgres SQL query expert. Given the following database schema:\n\n{payload.schema_content}\n\nWrite an optimized SQL query for this request: '{payload.query}'. Only provide the SQL code, without markdown formatting if possible."
        response = model.generate_content(prompt)
        return {"status": "success", "optimized_sql": response.text.strip()}
    except Exception as e:
        print("Error in advisor_chat:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schema/analyze", response_model=schemas.AnalyzeResponse)
def analyze_schema(payload: schemas.AnalyzeRequest):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Analyze the following database schema and provide performance recommendations (e.g., missing indexes, foreign keys, normalization). Return only a bulleted list (one point per line). Schema:\n\n{payload.schema_content}"
        response = model.generate_content(prompt)
        
        # Parse the bullet points into a list of strings
        recommendations = [line.strip().lstrip('-').lstrip('*').strip() for line in response.text.split('\n') if line.strip()]
        
        return {"status": "success", "recommendations": recommendations}
    except Exception as e:
        print("Error in analyze_schema:", e)
        raise HTTPException(status_code=500, detail=str(e))



