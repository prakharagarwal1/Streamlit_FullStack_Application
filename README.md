# 🚀 Streamlit FullStack Python Demo

A **complete full-stack Python application** demonstrating modern tooling:

- **Frontend**: Streamlit (multi-page app)
- **Backend**: FastAPI (async SQLAlchemy, JWT auth, Celery tasks)
- **Storage**: SQLite (dev) / Redis (Celery)
- **Charts**: Plotly, Matplotlib, Seaborn, WordCloud, ECharts, AgGrid
- **Deployment**: Docker Compose

---

## 📂 Project Structure

```
Streamlit_FullStack_Python/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── app/
│       ├── main.py              # FastAPI entry point
│       ├── config.py            # Pydantic settings
│       ├── database.py          # Async engine + session
│       ├── security.py          # JWT, bcrypt, rate limiting
│       ├── enums.py             # Enums + mixins
│       ├── exceptions.py        # Exception hierarchy + handlers
│       ├── models/              # SQLAlchemy models
│       │   ├── user.py
│       │   ├── product.py
│       │   ├── order.py
│       │   ├── post.py
│       │   ├── file.py
│       │   ├── api_key.py
│       │   ├── activity.py
│       │   └── task.py
│       ├── schemas/             # Pydantic schemas
│       ├── services/            # Business logic
│       ├── routers/             # API routes
│       ├── tasks/               # Celery tasks
│       └── utils/               # Helpers (pagination, charts, http)
├── frontend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── app.py                   # Streamlit entry point
│   ├── utils.py                 # API client helpers
│   └── pages/                   # Streamlit pages
│       ├── 01_auth.py
│       ├── 02_dashboard.py
│       ├── 03_charts.py
│       ├── 04_products.py
│       ├── 05_orders.py
│       ├── 06_blog.py
│       ├── 07_files.py
│       ├── 08_tasks.py
│       ├── 09_ai.py
│       └── 10_admin.py
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Tech Stack

### Backend

| Library                                    | Purpose             |
| ------------------------------------------ | ------------------- |
| **FastAPI**                                | Async web framework |
| **SQLAlchemy 2.0**                         | Async ORM           |
| **aiosqlite**                              | Async SQLite driver |
| **Pydantic / Pydantic-Settings**           | Validation + config |
| **Passlib + bcrypt**                       | Password hashing    |
| **python-jose**                            | JWT tokens          |
| **SlowAPI**                                | Rate limiting       |
| **Celery + Redis**                         | Background tasks    |
| **Pandas / Matplotlib / Seaborn / Plotly** | Data + charts       |
| **Prometheus Client**                      | Metrics             |
| **StructLog**                              | Structured logging  |

### Frontend

| Library                           | Purpose         |
| --------------------------------- | --------------- |
| **Streamlit 1.46**                | Multi-page UI   |
| **Plotly / Matplotlib / Seaborn** | Charts          |
| **WordCloud**                     | Word clouds     |
| **streamlit-echarts**             | Apache ECharts  |
| **streamlit-aggrid**              | Data grids      |
| **streamlit-modal / components**  | UI enhancements |

---

## 🚀 Quick Start (Docker Compose)

```bash
# 1. Copy env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. Start all services
docker compose up --build

# 3. Open in browser
# Frontend: http://localhost:8501
# Backend API docs: http://localhost:8000/docs
```

---

## 🧪 Manual Development Run

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
cp .env.example .env
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔐 Default Admin Account

After starting, register via the Auth page, then update the user's role to `admin` directly in the database:

```sql
UPDATE "user" SET role='admin' WHERE email='your@email.com';
```

---

## 📚 What You'll Learn

1. **FastAPI** — async endpoints, dependency injection, Pydantic schemas, exception handlers, CORS, OpenAPI docs
2. **SQLAlchemy 2.0** — async models, relationships, mixins, soft-delete patterns
3. **Authentication** — JWT access/refresh tokens, bcrypt, role-based access
4. **Streamlit** — multi-page apps, session state, forms, widgets, callbacks
5. **Charts** — Plotly interactive charts, Matplotlib static, Seaborn stats, WordCloud, ECharts
6. **Background Tasks** — Celery with Redis broker, task tracking in DB
7. **File Uploads** — multipart uploads, categorization, local storage
8. **Docker** — multi-service compose, healthchecks, volume persistence
9. **Production concerns** — rate limiting, request logging, metrics, error handling

---

## 📄 License

MIT — built for learning purposes.
