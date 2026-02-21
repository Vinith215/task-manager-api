# Task Manager API

A RESTful task management API built with **FastAPI**, **PostgreSQL (Supabase)**, **Redis**, and **Docker**. This project is the foundation for learning AI agent infrastructure — covering database design, caching patterns, containerization, and API development.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Database | PostgreSQL via Supabase |
| ORM | SQLAlchemy |
| Cache | Redis (cache-aside pattern) |
| Containerization | Docker + Docker Compose |
| Language | Python 3.11 |

---

## Project Structure

```
task-manager-api/
├── app/
│   ├── __init__.py
│   ├── main.py        # API routes and app entry point
│   ├── database.py    # SQLAlchemy engine and session setup
│   ├── models.py      # Task database model
│   └── cache.py       # Redis cache helpers
├── .env               # Environment variables (never commit this)
├── .gitignore
├── docker-compose.yml # Multi-container setup (API + Redis)
├── Dockerfile         # API container definition
└── requirements.txt   # Python dependencies
```

---

## Prerequisites

Before running this project, make sure you have installed:

- [Python 3.11+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- [Git](https://git-scm.com/)
- A [Supabase](https://supabase.com/) account with a project created

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/task-manager-api.git
cd task-manager-api
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```dotenv
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.YOUR-PROJECT-ID.supabase.co:5432/postgres
REDIS_URL=redis://localhost:6379
```

> Get your `DATABASE_URL` from Supabase → **Settings → Database → Connection String (URI)**.

### 3. Create the Supabase `tasks` Table

In your Supabase dashboard → **Table Editor → New Table**, create a table named `tasks` with these columns:

| Column | Type | Default |
|---|---|---|
| id | int8 | auto-increment |
| title | text | — |
| status | text | `'pending'` |
| created_at | timestamptz | `now()` |

---

## Running the App

### Option A — Local (Without Docker)

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start Redis via Docker (just Redis)
docker run -d -p 6379:6379 redis:7-alpine

# Start the API
uvicorn app.main:app --reload
```

### Option B — Fully Containerized (Docker Compose)

```bash
docker-compose up --build
```

This starts both the **API** and **Redis** containers together.

> API will be available at **http://localhost:8000**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/tasks` | Create a new task |
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{id}` | Get a single task (cached) |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

### Interactive API Docs

FastAPI auto-generates documentation at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Example Requests

**Create a task**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "status": "pending"}'
```

**Get a task (with caching)**
```bash
curl http://localhost:8000/tasks/1
# First call → Cache MISS (reads from DB, stores in Redis)
# Second call → Cache HIT (reads from Redis)
```

**Update a task**
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

**Delete a task**
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

---

## Caching Architecture

This project implements the **cache-aside pattern**:

```
GET /tasks/{id}
      │
      ▼
 Check Redis ──── HIT ──▶ Return cached data
      │
     MISS
      │
      ▼
 Query Postgres
      │
      ▼
 Store in Redis (TTL: 5 min)
      │
      ▼
 Return data
```

When a task is **updated or deleted**, its cache entry is immediately invalidated to prevent stale reads.

---

## Key Concepts Learned

- **PostgreSQL via SQLAlchemy** — defining models, running queries, managing sessions
- **REST API design** — CRUD endpoints, HTTP methods, status codes
- **Cache-aside pattern** — check cache first, fall back to DB, invalidate on write
- **Docker** — packaging an app into a portable container image
- **Docker Compose** — orchestrating multiple containers (API + Redis) as one stack

---

## Environment Variables Reference

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection URI from Supabase |
| `REDIS_URL` | Redis connection URI (default: `redis://localhost:6379`) |

---

## Stopping the App

```bash
# If using Docker Compose
docker-compose down

# To also remove volumes (clears Redis data)
docker-compose down -v
```

---

## Next Steps

This foundation is intentionally minimal. The next stages build on top of this infrastructure by adding:

- **Stage 2:** LLM integration — natural language task creation via OpenAI/Anthropic APIs
- **Stage 3:** AI agents — autonomous task planning and execution
- **Stage 4:** Multi-agent systems — coordinated agents with shared memory

---

## License

MIT
