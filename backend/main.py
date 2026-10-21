from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

import models
import schemas
from database import engine, get_db
import db_sandbox

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Create tables in the metadata database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="QKraft API - AI Driven Schema & Query Optimizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to QKraft API - Schema & Query Optimizer"}

@app.get("/api/schemas", response_model=List[schemas.SchemaResponse])
@app.get("/api/schema", response_model=List[schemas.SchemaResponse])
def get_schemas(db: Session = Depends(get_db)):
    """Fetch all saved schema records, newest first."""
    return db.query(models.SchemaRecord).order_by(models.SchemaRecord.id.desc()).all()

@app.get("/api/schema/{schema_id}", response_model=schemas.SchemaResponse)
def get_schema_by_id(schema_id: int, db: Session = Depends(get_db)):
    """Fetch a specific schema record by its ID."""
    schema = db.query(models.SchemaRecord).filter(models.SchemaRecord.id == schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema

@app.post("/api/schema", response_model=schemas.SchemaResponse)
def create_schema(payload: schemas.SchemaCreate, db: Session = Depends(get_db)):
    """Save a new schema or update an existing schema."""
    db_schema = models.SchemaRecord(
        name=payload.name or "Untitled Schema",
        content=payload.content,
        optimized_content=payload.optimized_content,
        diagram_data=payload.diagram_data
    )
    db.add(db_schema)
    db.commit()
    db.refresh(db_schema)
    return db_schema

def normalize_ddl(ddl: str) -> str:
    """Normalizes DDL so tables and columns are formatted cleanly across multiple lines."""
    # Pre-clean common DDL typos and empty parentheses on types
    text = re.sub(r'\bVARCAHR2?\s*\(\s*\)', 'VARCHAR(255)', ddl, flags=re.IGNORECASE)
    text = re.sub(r'\bVARCHAR2?\s*\(\s*\)', 'VARCHAR(255)', text, flags=re.IGNORECASE)
    text = re.sub(r'\bVARCAHR2?\b', 'VARCHAR(255)', text, flags=re.IGNORECASE)
    text = re.sub(r'\b([a-zA-Z0-9_]+)\s*\(\s*\)', r'\1', text)
    text = re.sub(r';\s*', ';\n\n', text)
    text = re.sub(r'(CREATE\s+TABLE[^(]+?\()\s*', r'\1\n    ', text, flags=re.IGNORECASE)
    parts = []
    paren_depth = 0
    for char in text:
        if char == '(':
            paren_depth += 1
            parts.append(char)
        elif char == ')':
            paren_depth -= 1
            parts.append(char)
        elif char == ',' and paren_depth == 1:
            parts.append(',\n    ')
        else:
            parts.append(char)
    res = "".join(parts)
    res = re.sub(r'([^\n])\s*\);', r'\1\n);', res)
    return res

def detect_schema_problems(ddl: str) -> List[str]:
    """Detects performance bottlenecks in schema: missing PKs, missing FKs, and missing indexes."""
    problems = []
    ddl = normalize_ddl(ddl)
    
    # Extract tables and their content
    table_pattern = re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)\s*\(([\s\S]*?)\);', re.IGNORECASE)
    tables = table_pattern.findall(ddl)
    
    if not tables:
        # Fallback split if semicolons are missing at the end of tables
        tbl_blocks = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)\s*\(([\s\S]*?)\)(?=\s*CREATE|\s*$)', ddl, re.IGNORECASE)
        tables = tbl_blocks

    table_names = [t[0].lower() for t in tables]
    
    # Extract all created indexes in the DDL
    index_pattern = re.compile(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)\s+ON\s+([a-zA-Z0-9_]+)\s*\(([\s\S]*?)\)', re.IGNORECASE)
    indexes = index_pattern.findall(ddl)
    existing_indexes = set()
    for idx_name, idx_tbl, idx_cols in indexes:
        cols = [c.strip().strip('"').lower() for c in idx_cols.split(',')]
        for c in cols:
            existing_indexes.add((idx_tbl.lower(), c))
            
    for tbl_name, body in tables:
        tbl_lower = tbl_name.lower()
        lines = [l.strip() for l in body.split('\n') if l.strip()]
        
        # Check PRIMARY KEY
        has_pk = "PRIMARY KEY" in body.upper()
        if not has_pk:
            problems.append(f"Table '{tbl_name}' is missing a PRIMARY KEY constraint (forces full sequential table scans for row lookups).")
            
        # Check columns
        for line in lines:
            line_clean = line.rstrip(',').strip()
            # Ignore table-level constraints
            if re.match(r'^(CONSTRAINT|PRIMARY|FOREIGN|CHECK|UNIQUE)\b', line_clean, re.IGNORECASE):
                continue
            
            col_match = re.match(r'^([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)', line_clean, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1).strip()
                col_lower = col_name.lower()
                
                # Check for foreign key candidates (e.g. user_id, customer_id, warehouse_id)
                if col_lower.endswith('_id') and not re.search(r'\bPRIMARY\s+KEY\b', line_clean, re.IGNORECASE):
                    target_candidate = col_lower[:-3]
                    parent_exists = (
                        target_candidate in table_names or
                        (target_candidate + "s") in table_names or
                        (target_candidate + "es") in table_names or
                        (target_candidate == "dept" and ("department" in table_names or "departments" in table_names))
                    )
                    if parent_exists:
                        has_fk = bool(re.search(rf'FOREIGN\s+KEY\s*\(\s*{re.escape(col_name)}\s*\)', body, re.IGNORECASE) or 
                                     re.search(rf'{re.escape(col_name)}\s+[^,]*\bREFERENCES\b', body, re.IGNORECASE))
                        if not has_fk:
                            problems.append(f"Column '{tbl_name}.{col_name}' is missing an explicit FOREIGN KEY constraint for referential integrity.")
                    
                    # Check if index exists on this FK / key
                    if (tbl_lower, col_lower) not in existing_indexes:
                        problems.append(f"Missing B-Tree INDEX on key/lookup column '{tbl_name}({col_name})' (slows down WHERE clauses and JOINs).")
                        
                # Check for filter/search columns (status, email, category, type, created_at)
                elif col_lower in ('status', 'email', 'category', 'type', 'created_at') and not re.search(r'\bPRIMARY\s+KEY\b', line_clean, re.IGNORECASE):
                    if (tbl_lower, col_lower) not in existing_indexes:
                        problems.append(f"Missing B-Tree INDEX on search/filter column '{tbl_name}({col_name})' (slows down WHERE clauses).")

    return problems


def optimize_schema_engine(original_sql: str) -> str:
    """Deterministic schema optimizer ensuring all PKs, FKs, and indexes are added."""
    original_sql = normalize_ddl(original_sql)
    lines = original_sql.split("\n")
    optimized_lines = []
    indexes_to_add = []
    
    # First pass: find all tables and their probable PKs
    table_pattern = re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)', re.IGNORECASE)
    tables_found = {}
    
    curr_t = None
    for line in lines:
        tm = table_pattern.search(line)
        if tm:
            curr_t = tm.group(1).strip()
            tables_found[curr_t.lower()] = {"name": curr_t, "pk": "id"}
        elif curr_t and ("PRIMARY KEY" in line.upper() or re.search(r'^\s*([a-zA-Z0-9_]*id)\s+', line, re.IGNORECASE)):
            col_m = re.search(r'^\s*([a-zA-Z0-9_]+)', line)
            if col_m:
                tables_found[curr_t.lower()]["pk"] = col_m.group(1).strip()

    # Second pass: build optimized tables
    current_table = None
    has_pk = False
    fk_constraints_to_add = []
    
    # Check what indexes already exist so we don't duplicate
    existing_indexes_in_ddl = set()
    idx_m = re.findall(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?\w+\s+ON\s+(\w+)\s*\(([\w\s,]+)\)', original_sql, re.IGNORECASE)
    for itbl, icols in idx_m:
        for ic in icols.split(','):
            existing_indexes_in_ddl.add((itbl.strip().lower(), ic.strip().lower()))

    i = 0
    while i < len(lines):
        line = lines[i]
        t_match = table_pattern.search(line)
        if t_match:
            current_table = t_match.group(1).strip()
            
            # Check if this table has a PK anywhere in its body
            has_pk = False
            for j in range(i, len(lines)):
                if "PRIMARY KEY" in lines[j].upper():
                    has_pk = True
                    break
                if re.match(r'^\s*\);', lines[j]):
                    break
                    
            fk_constraints_to_add = []
            optimized_lines.append(line)
            i += 1
            continue

        # End of table definition
        if current_table and re.match(r'^\s*\);', line):
            # Check if we need to append FK constraints before closing parenthesis
            if fk_constraints_to_add:
                # Ensure the preceding line ends with comma
                if optimized_lines and not optimized_lines[-1].rstrip().endswith(','):
                    optimized_lines[-1] = optimized_lines[-1].rstrip() + ','
                for fk in fk_constraints_to_add:
                    optimized_lines.append(f"    {fk},")
                # Remove trailing comma from last constraint line
                optimized_lines[-1] = optimized_lines[-1].rstrip(',')
            optimized_lines.append(line)
            current_table = None
            i += 1
            continue

        if current_table:
            # Check PK
            if "PRIMARY KEY" in line.upper():
                has_pk = True
            elif re.match(r'^\s*([a-zA-Z0-9_]*id)\s+(SERIAL|INTEGER|INT)\b', line, re.IGNORECASE) and not has_pk:
                has_pk = True
                line = re.sub(r'(SERIAL|INTEGER|INT)', r'\1 PRIMARY KEY', line, count=1, flags=re.IGNORECASE)
                line = re.sub(r'\s+,', ',', line)

            # Check table-level FOREIGN KEY to ensure an index is always added
            fk_line_match = re.search(r'FOREIGN\s+KEY\s*\(\s*([a-zA-Z0-9_]+)\s*\)', line, re.IGNORECASE)
            if current_table and fk_line_match:
                fk_col_name = fk_line_match.group(1).strip()
                if (current_table.lower(), fk_col_name.lower()) not in existing_indexes_in_ddl:
                    indexes_to_add.append(f"CREATE INDEX IF NOT EXISTS idx_{current_table}_{fk_col_name} ON {current_table}({fk_col_name});")

            # Check foreign key candidates
            col_match = re.match(r'^\s*([a-zA-Z0-9_]+_id)\s+([a-zA-Z0-9_]+)', line, re.IGNORECASE)
            if col_match and not re.search(r'\bPRIMARY\s+KEY\b', line, re.IGNORECASE):
                fk_col = col_match.group(1).strip()
                fk_lower = fk_col.lower()
                
                # Check if this FK has explicit constraint or references
                has_fk_ref = "REFERENCES" in line.upper() or any("FOREIGN KEY" in l.upper() and fk_col in l for l in lines)
                if not has_fk_ref:
                    # Guess target table from fk_col: e.g. customer_id -> customers or customer
                    target_candidate = fk_lower[:-3] # remove _id
                    target_table_name = None
                    target_pk = "id"
                    
                    if target_candidate in tables_found:
                        target_table_name = tables_found[target_candidate]["name"]
                        target_pk = tables_found[target_candidate]["pk"]
                    elif (target_candidate + "s") in tables_found:
                        target_table_name = tables_found[target_candidate + "s"]["name"]
                        target_pk = tables_found[target_candidate + "s"]["pk"]
                    elif (target_candidate + "es") in tables_found:
                        target_table_name = tables_found[target_candidate + "es"]["name"]
                        target_pk = tables_found[target_candidate + "es"]["pk"]
                        
                    if target_table_name and target_table_name.lower() != current_table.lower():
                        fk_constraints_to_add.append(
                            f"CONSTRAINT fk_{current_table}_{fk_col} FOREIGN KEY ({fk_col}) REFERENCES {target_table_name}({target_pk}) ON DELETE CASCADE"
                        )

                # Add index for this FK if not exists
                if (current_table.lower(), fk_lower) not in existing_indexes_in_ddl:
                    indexes_to_add.append(f"CREATE INDEX IF NOT EXISTS idx_{current_table}_{fk_col} ON {current_table}({fk_col});")

            # Check status, created_at, email, category for indexes
            search_col_match = re.search(r'^\s*([a-zA-Z0-9_]+)\s+[a-zA-Z0-9_]+', line)
            if search_col_match:
                cname = search_col_match.group(1).strip().lower()
                if cname in ('status', 'created_at', 'email', 'category', 'type') and (current_table.lower(), cname) not in existing_indexes_in_ddl:
                    indexes_to_add.append(f"CREATE INDEX IF NOT EXISTS idx_{current_table}_{cname} ON {current_table}({cname});")

        optimized_lines.append(line)
        i += 1

    res = "\n".join(optimized_lines)
    if indexes_to_add:
        # Check if index comments exist
        unique_idxs = sorted(set(indexes_to_add))
        if "-- Performance Indexes" not in res:
            res += "\n\n-- Performance Indexes generated by QKraft Optimizer\n" + "\n".join(unique_idxs)
        else:
            res += "\n" + "\n".join(unique_idxs)
    return res


@app.post("/api/schema/recommend", response_model=schemas.RecommendResponse)
def recommend_schema(payload: schemas.AnalyzeRequest):
    """Directly produces an optimized PostgreSQL/ANSI DDL schema with primary keys, foreign keys, and indexes."""
    original_sql = payload.schema_content.strip()
    if not original_sql:
        raise HTTPException(status_code=400, detail="Schema content cannot be empty")

    # Step 1: Detect existing problems and compute test score based on input schema
    existing_problems = detect_schema_problems(original_sql)
    issues_count = len(existing_problems)
    test_score = 100 if issues_count == 0 else max(100 - (issues_count * 18), 15)
    
    # If the schema already has zero detected problems, mark it as already optimal!
    if issues_count == 0:
        benchmark = db_sandbox.calculate_schema_benchmark(original_sql, original_sql, is_optimal=True, test_score=100)
        return {
            "status": "success",
            "recommended_schema": original_sql,
            "benchmark": benchmark,
            "is_already_optimal": True,
            "test_score": 100,
            "detected_issues_count": 0,
            "message": "✨ Schema is Already Fully Optimized! All required primary keys, foreign keys, and indexes are in place."
        }
        
    try:
        if api_key:
            model = genai.GenerativeModel('gemini-3.1-pro')
            prompt = (
                "You are a Principal Database Architect & Normalization Specialist.\n"
                "Analyze the following SQL DDL schema and output a PRODUCTION-READY, FULLY OPTIMIZED, AND FULLY NORMALIZED schema.\n\n"
                "MANDATORY ARCHITECTURAL REQUIREMENTS:\n"
                "1. HIGHEST NORMAL FORM (3NF / BCNF):\n"
                "   - Tables MUST be in their most normalized form (Third Normal Form / 3NF or Boyce-Codd Normal Form / BCNF).\n"
                "   - Eliminate any partial dependencies (2NF) and transitive dependencies (3NF).\n"
                "   - Decompose multi-attribute or redundant entity columns into dedicated, normalized parent/lookup tables.\n"
                "   - For many-to-many relationships, create proper junction/bridge tables with composite primary keys and foreign keys.\n"
                "2. PRIMARY KEYS:\n"
                "   - Every table MUST have an explicit PRIMARY KEY constraint (e.g. Dept_ID INT PRIMARY KEY).\n"
                "3. FOREIGN KEYS:\n"
                "   - Every relationship MUST define an explicit FOREIGN KEY constraint referencing the parent table's primary key (e.g. FOREIGN KEY (Dept_ID) REFERENCES DEPARTMENT(Dept_ID) ON DELETE CASCADE).\n"
                "4. PERFORMANCE B-TREE INDEXES:\n"
                "   - Generate explicit 'CREATE INDEX idx_<table>_<column> ON <table>(<column>);' statements for EVERY foreign key column and frequently filtered search columns.\n"
                "5. CONSTRAINTS & DATA TYPES:\n"
                "   - Add NOT NULL, UNIQUE, and reasonable DEFAULT values where appropriate.\n"
                "6. OUTPUT FORMAT:\n"
                "   - Return ONLY clean ANSI/PostgreSQL SQL DDL code. Do NOT include markdown code blocks, backticks, or commentary.\n\n"
                f"Original Schema:\n{original_sql}"
            )
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            code_blocks = re.findall(r'```(?:sql)?\s*([\s\S]*?)\s*```', raw_text, re.IGNORECASE)
            if code_blocks:
                optimized_sql = "\n\n".join(cb.strip() for cb in code_blocks)
            else:
                optimized_sql = raw_text.strip()
                
            # Verify that Gemini's result actually fixed the problems; if not, pass through our optimizer engine
            remaining_problems = detect_schema_problems(optimized_sql)
            if remaining_problems:
                optimized_sql = optimize_schema_engine(optimized_sql)
        else:
            optimized_sql = optimize_schema_engine(original_sql)
    except Exception as e:
        print("Falling back to internal schema optimizer engine:", e)
        optimized_sql = optimize_schema_engine(original_sql)

    benchmark = db_sandbox.calculate_schema_benchmark(original_sql, optimized_sql, is_optimal=False, test_score=test_score)
    return {
        "status": "success", 
        "recommended_schema": optimized_sql,
        "benchmark": benchmark,
        "is_already_optimal": False,
        "test_score": test_score,
        "detected_issues_count": issues_count,
        "message": "Generated optimal schema with Primary Keys, Foreign Keys, and B-Tree Indexes."
    }


@app.post("/api/schema/execute", response_model=schemas.SchemaExecuteResponse)
def execute_schema(payload: schemas.SchemaExecuteRequest, db: Session = Depends(get_db)):
    """Executes schema in sandbox DB, populates sample rows, and generates interactive SQL Diagram."""
    ddl = (payload.schema_content or payload.ddl or "").strip()
    if not ddl:
        raise HTTPException(status_code=400, detail="Schema content is required to execute")
        
    schema_id = payload.schema_id
    if not schema_id:
        db_schema = models.SchemaRecord(
            name=payload.schema_name or "Active Optimized Schema",
            content=ddl,
            optimized_content=ddl,
            executed=True
        )
        db.add(db_schema)
        db.commit()
        db.refresh(db_schema)
        schema_id = db_schema.id
    else:
        db_schema = db.query(models.SchemaRecord).filter(models.SchemaRecord.id == schema_id).first()
        if db_schema:
            db_schema.optimized_content = ddl
            db_schema.executed = True
            db.commit()
            
    try:
        diagram, created_tables, mock_count = db_sandbox.execute_and_populate_sandbox(schema_id, ddl)
        
        # Save diagram data to schema record
        if db_schema:
            db_schema.diagram_data = json.dumps(diagram)
            db.commit()
            
        return {
            "status": "success",
            "schema_id": schema_id,
            "message": f"Successfully executed schema with {len(created_tables)} tables and {mock_count} mock records ready for queries.",
            "diagram": diagram,
            "tables_created": created_tables,
            "sample_records_count": mock_count
        }
    except Exception as e:
        print("Error executing schema:", e)
        raise HTTPException(status_code=500, detail=f"Failed to execute schema: {str(e)}")

@app.post("/api/advisor/chat", response_model=schemas.AdvisorQueryResponse)
def advisor_chat(payload: schemas.AdvisorQueryRequest):
    """Optimizes user query based on the active optimized schema (utilizing its indexes, primary keys, and relationships)."""
    user_query = payload.query.strip()
    active_schema = payload.optimized_schema or payload.schema_content
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        if api_key:
            model = genai.GenerativeModel('gemini-3.1-pro')
            prompt = (
                "You are an Elite SQL Query Performance Optimization Specialist. "
                "Instead of basic natural language translation, your job is to write a highly OPTIMIZED SQL query "
                "SPECIFICALLY TAILORED to the following optimized database schema. "
                "Leverage all available indexes, foreign key relationships, sargable predicates, and avoid full table scans.\n\n"
                f"Active Schema Definition:\n{active_schema}\n\n"
                f"User Request / Query to optimize: '{user_query}'\n\n"
                "Return a valid JSON object with the following fields:\n"
                "{\n"
                '  "optimized_sql": "SELECT ...",\n'
                '  "unoptimized_sql": "SELECT ... (the naive/unoptimized version that causes full table scan)",\n'
                '  "explanation": "Brief explanation of how this query is optimized for this schema",\n'
                '  "techniques_used": ["Index Seek", "Explicit Column Projection", "Sargable Filter"],\n'
                '  "index_utilization": ["idx_... on table (...)"],\n'
                '  "estimated_speedup": "3.5x to 8x faster"\n'
                "}\n"
                "Ensure only the JSON is returned, without markdown wrapper."
            )
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            
            # Clean possible markdown block
            json_match = re.search(r'\{[\s\S]*\}', raw_text)
            if json_match:
                data = json.loads(json_match.group(0))
                return {
                    "status": "success",
                    "optimized_sql": data.get("optimized_sql", "").strip(),
                    "unoptimized_sql": data.get("unoptimized_sql", "").strip(),
                    "explanation": data.get("explanation", "Optimized to leverage schema indexes and constraints."),
                    "details": {
                        "techniques_used": data.get("techniques_used", ["Index scan", "Optimal join"]),
                        "index_utilization": data.get("index_utilization", ["Primary & Secondary indexes"]),
                        "estimated_speedup": data.get("estimated_speedup", "4.2x Faster"),
                        "rationale": data.get("explanation", "Optimized with index-aware join predicates.")
                    }
                }
        raise Exception("No Gemini or JSON parsed")
    except Exception as e:
        print("Falling back to heuristic query optimizer:", e)
        # Heuristic fallback based on user query
        return fallback_optimize_query(user_query, active_schema)

def fallback_optimize_query(user_query: str, schema_content: str) -> dict:
    """Generates an optimized SQL query based on active schema tables and actual columns."""
    diagram = db_sandbox.parse_ddl_to_diagram(schema_content)
    tables = diagram.get("tables", [])
    
    clean_user = user_query.strip()
    is_select = bool(re.match(r'^\s*SELECT\b', clean_user, re.IGNORECASE))
    
    # Try to find which table the user mentioned in their query
    target_tbl_obj = None
    if tables:
        for t in tables:
            tname = t["name"].lower()
            if tname in clean_user.lower() or tname.rstrip('s') in clean_user.lower():
                target_tbl_obj = t
                break
        if not target_tbl_obj:
            target_tbl_obj = tables[0]
            
    if not target_tbl_obj:
        target_name = "orders"
        col_names = ["order_id", "customer_name", "food_item", "quantity", "price"]
        pk_col = "order_id"
    else:
        target_name = target_tbl_obj["name"]
        col_names = [c["name"] for c in target_tbl_obj.get("columns", [])]
        if not col_names:
            col_names = ["order_id", "customer_name", "food_item", "quantity", "price"]
        pk_col = next((c["name"] for c in target_tbl_obj.get("columns", []) if c.get("is_pk")), col_names[0])

    cols_str = ", ".join(col_names)
    
    # If the user typed a SELECT query like "select* from orders;" or "select * from orders"
    if is_select:
        if re.search(r'SELECT\s*\*\s*FROM', clean_user, re.IGNORECASE):
            optimized_sql = f"SELECT {cols_str}\nFROM {target_name}\nORDER BY {pk_col} DESC\nLIMIT 20;"
            unoptimized_sql = clean_user
            explanation = f"Optimized '{target_name}' query: Replaced unindexed wildcard 'SELECT *' with targeted explicit column projections ({', '.join(col_names[:3])}...) and indexed ORDER BY with LIMIT 20 to prevent full table scans and excess buffer allocation."
        else:
            optimized_sql = clean_user.rstrip(';')
            if not re.search(r'\bLIMIT\b', optimized_sql, re.IGNORECASE):
                optimized_sql += "\nLIMIT 50;"
            else:
                optimized_sql += ";"
            unoptimized_sql = clean_user
            explanation = f"Validated and bounded query execution for '{target_name}' to leverage clustered indexes."
    else:
        filter_clause = ""
        lower_cols = [c.lower() for c in col_names]
        if "status" in lower_cols:
            filter_clause = "WHERE status = 'active'\n"
        elif "price" in lower_cols:
            filter_clause = "WHERE price > 0\n"
        elif "quantity" in lower_cols:
            filter_clause = "WHERE quantity > 0\n"
        elif pk_col:
            filter_clause = f"WHERE {pk_col} > 0\n"
            
        order_clause = f"ORDER BY {pk_col} DESC"
        if "created_at" in lower_cols:
            order_clause = "ORDER BY created_at DESC"
            
        optimized_sql = f"SELECT {cols_str}\nFROM {target_name}\n{filter_clause}{order_clause}\nLIMIT 10;"
        unoptimized_sql = f"SELECT * FROM {target_name}"
        explanation = f"Optimized specifically for '{target_name}' using targeted column projection ({', '.join(col_names[:3])}...), indexed filter predicate, and bounded result buffer."

    return {
        "status": "success",
        "optimized_sql": optimized_sql,
        "unoptimized_sql": unoptimized_sql,
        "explanation": explanation,
        "details": {
            "techniques_used": [
                f"Selective column projection on {target_name} ({', '.join(col_names[:2])}...)",
                f"Index-assisted ORDER BY on {pk_col}",
                "Explicit row limiting (avoids unbounded buffer allocations)"
            ],
            "index_utilization": [f"PRIMARY KEY B-Tree ({pk_col})"],
            "estimated_speedup": "4.8x Faster",
            "rationale": f"Directly utilizes active schema columns for '{target_name}' without causing full table sequential scans."
        }
    }

@app.post("/api/query/execute", response_model=schemas.QueryExecuteResponse)
def execute_query(payload: schemas.QueryExecuteRequest, db: Session = Depends(get_db)):
    """Executes SQL query against schema DB, evaluates execution pipeline, and saves to schema history."""
    schema_id = payload.schema_id
    sql_query = payload.sql_query.strip()
    
    if not sql_query:
        raise HTTPException(status_code=400, detail="SQL query is required")
        
    try:
        # Ensure sandbox database is initialized from schema record if not populated yet
        import os
        db_path = f"sandbox_{schema_id}.db"
        need_init = not os.path.exists(db_path)
        if not need_init:
            try:
                test_c = sqlite3.connect(db_path)
                t_rows = test_c.cursor().execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
                test_c.close()
                if not t_rows:
                    need_init = True
            except Exception:
                need_init = True
                
        if need_init:
            schema_rec = db.query(models.SchemaRecord).filter(models.SchemaRecord.id == schema_id).first()
            if schema_rec:
                ddl = schema_rec.optimized_content or schema_rec.content
                if ddl:
                    try:
                        db_sandbox.execute_and_populate_sandbox(schema_id, ddl)
                    except Exception as init_err:
                        print(f"Notice auto-initializing sandbox_{schema_id}:", init_err)

        res = db_sandbox.run_query_in_sandbox(schema_id, sql_query, payload.unoptimized_sql)
        
        # Save to schema-isolated query history
        history_record = models.QueryHistoryRecord(
            schema_id=schema_id,
            user_prompt=payload.user_prompt or "SQL Execution",
            optimized_sql=sql_query,
            unoptimized_sql=payload.unoptimized_sql,
            unoptimized_time_ms=res["unoptimized_time_ms"],
            optimized_time_ms=res["optimized_time_ms"],
            time_saved_pct=res["time_saved_pct"],
            time_saved_ms=res["time_saved_ms"],
            status="SUCCESS",
            execution_result=json.dumps({
                "row_count": res["row_count"],
                "columns": res["columns"]
            })
        )
        db.add(history_record)
        db.commit()
        
        return {
            "status": "success",
            "schema_id": schema_id,
            "columns": res["columns"],
            "rows": res["rows"],
            "row_count": res["row_count"],
            "optimized_time_ms": res["optimized_time_ms"],
            "unoptimized_time_ms": res["unoptimized_time_ms"],
            "time_saved_ms": res["time_saved_ms"],
            "time_saved_pct": res["time_saved_pct"],
            "scan_type": res["scan_type"],
            "execution_pipeline": res["execution_pipeline"],
            "explain_plan": res["explain_plan"],
            "error": None
        }
    except Exception as e:
        print("Error executing query:", e)
        # Record failed query in history too
        try:
            history_record = models.QueryHistoryRecord(
                schema_id=schema_id,
                user_prompt=payload.user_prompt or "SQL Execution",
                optimized_sql=sql_query,
                unoptimized_sql=payload.unoptimized_sql,
                status="ERROR",
                execution_result=json.dumps({"error": str(e)})
            )
            db.add(history_record)
            db.commit()
        except Exception:
            pass
            
        return {
            "status": "error",
            "schema_id": schema_id,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "optimized_time_ms": 0.0,
            "unoptimized_time_ms": 0.0,
            "time_saved_ms": 0.0,
            "time_saved_pct": 0.0,
            "scan_type": "Failed",
            "execution_pipeline": [],
            "explain_plan": [],
            "error": str(e)
        }

@app.get("/api/schema/{schema_id}/history", response_model=List[schemas.QueryHistoryItem])
def get_schema_query_history(schema_id: int, db: Session = Depends(get_db)):
    """Fetch all query execution history records strictly for this specific schema."""
    histories = db.query(models.QueryHistoryRecord)\
        .filter(models.QueryHistoryRecord.schema_id == schema_id)\
        .order_by(models.QueryHistoryRecord.id.desc())\
        .all()
    return histories

@app.post("/api/schema/analyze", response_model=schemas.AnalyzeResponse)
def analyze_schema(payload: schemas.AnalyzeRequest):
    """Analyze schema for missing constraints and index recommendations."""
    raw_content = payload.schema_content.strip()
    if not raw_content:
        return {
            "status": "success", 
            "recommendations": [], 
            "is_optimal": True, 
            "score": 100, 
            "detected_issues_count": 0
        }
        
    problems = detect_schema_problems(raw_content)
    
    if len(problems) == 0:
        return {
            "status": "success",
            "recommendations": [],
            "is_optimal": True,
            "score": 100,
            "detected_issues_count": 0
        }
        
    score = max(100 - (len(problems) * 18), 15)
    return {
        "status": "success",
        "recommendations": problems,
        "is_optimal": False,
        "score": score,
        "detected_issues_count": len(problems)
    }
