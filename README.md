# QKraft: AI-Driven Database Schema and Query Advisor

[![Java](https://img.shields.io/badge/Java-23-ED8B00?style=flat&logo=openjdk&logoColor=white)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.3.5-6DB33F?style=flat&logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

**QKraft** is an intelligent database schema optimization and SQL query advising platform. It analyzes relational schemas (DDL), diagnoses anti-patterns, recommends missing constraints and indexes, visualizes entity-relationship structures, and safely tests query rewrites inside isolated PostgreSQL sandboxes.

---

## Key Features

- **Automated Schema Diagnostics**: Identifies missing primary keys, unindexed foreign key lookups, non-normalized attributes, and missing search indexes.
- **Intelligent Query Advisor**:
  - Rewrites non-SARGable predicates (e.g., `UPPER(col) = 'val'` to `col ILIKE 'val'`).
  - Eliminates inefficient `SELECT *` wildcard projections.
  - Bounds memory allocation by adding indexed `ORDER BY` and `LIMIT` clauses to avoid expensive disk spills (`work_mem`).
  - Converts implicit comma cross joins into explicit ANSI `INNER JOIN` clauses.
- **Isolated PostgreSQL Sandbox Execution**:
  - Automatically provisions dedicated `sandbox_<schema_id>` PostgreSQL schemas per project.
  - Synthesizes realistic mock data across tables to evaluate queries under real execution conditions.
  - Measures execution times (`ms`), computes speedup multipliers, and displays PostgreSQL execution plans.
- **Interactive Schema Visualizer**: Extracts and renders entity-relationship diagrams (ERD) with primary/foreign key connections directly from raw DDL.
- **Query History & Comparative Benchmarks**: Tracks execution histories, before/after runtimes, and performance deltas.
- **Dual Interface Options**:
  - **Embedded Dashboard**: Pre-packaged, lightweight dashboard served directly from the Spring Boot server (`http://localhost:8000`).
  - **Decoupled Next.js UI**: Modern Next.js 15 + TypeScript web application (`http://localhost:3000`).

---

## Architecture Overview

```
                               ┌──────────────────────────────────────────────┐
                               │                 User Clients                 │
                               │  - Next.js Frontend (Port 3000)              │
                               │  - Embedded Static Web UI (Port 8000)        │
                               └──────────────────────┬───────────────────────┘
                                                      │ REST API
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │         Spring Boot Backend (Port 8000)       │
                               │ ───────────────────────────────────────────  │
                               │ • DdlParserService     (AST & ERD Extraction)│
                               │ • SchemaOptimizerService (Index/Constraint)  │
                               │ • QueryAdvisorService    (Anti-Pattern Lint) │
                               │ • SandboxExecutionService(Schema Isolation)  │
                               └──────────────────────┬───────────────────────┘
                                                      │ JDBC
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │             PostgreSQL Database              │
                               │ ───────────────────────────────────────────  │
                               │ • public schema      (Schemas, Query History)│
                               │ • sandbox_<id>       (Isolated Execution)    │
                               └──────────────────────────────────────────────┘
```

Detailed architectural diagrams are available in the [`diagrams/`](diagrams/) directory:
- `diagrams/dfd_level_0.png` — Context-level data flow diagram.
- `diagrams/dfd_level_1.png` — Subsystem decomposition and data flow.
- `diagrams/dfd_level_2.png` — Deep-dive sandbox execution engine workflow.
- `diagrams/qkraft_pipeline_workflow.png` — End-to-end schema ingestion and query optimization pipeline.

---

## Tech Stack

| Component | Technologies |
| :--- | :--- |
| **Backend** | Java 23, Spring Boot 3.3.5, Spring Data JPA, Hibernate, PostgreSQL JDBC |
| **Frontend (Decoupled)** | Next.js 15, React 19, TypeScript, CSS Modules, Lucide Icons |
| **Frontend (Embedded)** | Vanilla HTML5, Modern CSS3, JavaScript (ES6+), Canvas ERD |
| **Database** | PostgreSQL 16 |
| **DevOps** | Docker, Docker Compose, Multi-stage builds |

---

## Quick Start

### Option 1: Run with Docker Compose (Recommended)

Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop) installed:

```bash
# Clone the repository
git clone https://github.com/joydeepmandal26/QKraft-AI-Driven-Schema-and-Query-Advisor.git
cd QKraft-AI-Driven-Schema-and-Query-Advisor

# Start PostgreSQL, Spring Boot backend, and Next.js frontend
docker compose up --build
```

- **Next.js Web App**: [http://localhost:3000](http://localhost:3000)
- **Spring Boot Embedded UI & API**: [http://localhost:8000](http://localhost:8000)
- **PostgreSQL**: `localhost:5432` (`qkraft` database)

---

### Option 2: Run Locally (Without Docker)

#### Prerequisites
- **Java 21 or 23 JDK**
- **Maven 3.9+**
- **PostgreSQL 15+** running locally on port 5432
- **Node.js 20+** (if running the Next.js frontend)

#### Step 1: Create PostgreSQL Database
In `psql` or pgAdmin:
```sql
CREATE DATABASE qkraft;
```

#### Step 2: Run the Spring Boot Backend
On Windows:
```cmd
start.bat
```
Or with Maven directly:
```bash
cd springboot-backend
mvn spring-boot:run
```
The backend server and embedded web interface are now live at [http://localhost:8000](http://localhost:8000).

#### Step 3 (Optional): Run the Next.js Frontend
```bash
cd frontend
npm install
npm run dev
```
The Next.js interface is live at [http://localhost:3000](http://localhost:3000).

---

## Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Port for the Spring Boot server |
| `SPRING_DATASOURCE_URL` | `jdbc:postgresql://localhost:5432/qkraft` | PostgreSQL JDBC connection URL |
| `SPRING_DATASOURCE_USERNAME` | `postgres` | PostgreSQL username |
| `SPRING_DATASOURCE_PASSWORD` | `system` | PostgreSQL password |
| `BACKEND_URL` | `http://127.0.0.1:8000` | Target URL used by Next.js API proxy rewrite |

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check endpoint returning API status |
| `GET` | `/api/schemas` | Fetch all saved schemas and their optimization states |
| `GET` | `/api/schema/{id}` | Fetch a specific schema record by ID |
| `POST` | `/api/schema` | Save or update a schema record with ERD metadata |
| `POST` | `/api/schema/recommend` | Analyze raw DDL, detect anti-patterns, and generate optimized schema |
| `POST` | `/api/schema/execute` | Provision an isolated PostgreSQL sandbox (`sandbox_<id>`) and seed mock data |
| `POST` | `/api/advisor/chat` | Analyze SQL queries or natural language queries and provide optimized rewrites |
| `POST` | `/api/query/execute` | Execute query in sandbox, measure real execution time, and record history |
| `GET` | `/api/schema/{id}/history` | Retrieve query execution benchmarks and historical runtimes |
| `DELETE` | `/api/schema/{id}` | Delete a schema and its associated query history |

---

## Deployment Guide

### Deploying Backend to Cloud (Railway / Render / AWS)
1. Link your GitHub repository to your cloud provider.
2. Set the root directory to `springboot-backend`.
3. Provision a managed **PostgreSQL** database.
4. Set the following environment variables:
   - `SPRING_DATASOURCE_URL` (e.g. `jdbc:postgresql://<host>:<port>/<dbname>`)
   - `SPRING_DATASOURCE_USERNAME`
   - `SPRING_DATASOURCE_PASSWORD`
   - `PORT` (configured automatically by cloud providers)

### Deploying Frontend to Vercel
1. Import the repository into [Vercel](https://vercel.com).
2. Set the root directory to `frontend`.
3. Set the environment variable:
   - `BACKEND_URL`: `https://your-deployed-backend-url.com`

---

## License

This project is licensed under the [MIT License](LICENSE).
