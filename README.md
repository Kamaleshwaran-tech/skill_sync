<<<<<<< HEAD
# SkillSync AI

SkillSync AI is an AI-powered Career Guidance and Live Job Skill Matching Platform designed for students. It offers resume analysis, semantic job matching, skill gap analysis, career readiness scoring, and personalized learning roadmaps.

---

## 🏛️ Architecture Summary

- **Backend**: FastAPI + SQLAlchemy ORM + Alembic + Pydantic v2
- **AI / NLP Stack**: spaCy + PyMuPDF + Sentence Transformers (`all-MiniLM-L6-v2`) + NumPy / scikit-learn Cosine Similarity + Google Gemini API
- **Frontend**: React 19 + Vite + Material-UI (MUI) + Recharts + Framer Motion
- **Database**: Universal support for PostgreSQL, MySQL 8, or zero-config local SQLite (`skillsync_ai.db`)

---

## 🚀 Getting Started Locally

### 1. Start the Backend API (FastAPI)

```powershell
# Navigate to the backend directory
cd backend

# Activate the virtual environment (Windows PowerShell)
.\.venv\Scripts\activate

# (Optional: install dependencies if needed)
pip install -r requirements.txt

# Start the FastAPI development server on port 8000
uvicorn app.main:app --reload --port 8000
```

The API is accessible at:
- **Interactive Swagger Docs**: `http://localhost:8000/api/v1/docs`
- **ReDoc Documentation**: `http://localhost:8000/api/v1/redoc`
- **Health Check**: `http://localhost:8000/api/v1/health`

---

### 2. Start the Frontend (React + Vite)

In a separate terminal window:

```powershell
# Navigate to the frontend directory
cd frontend

# Install frontend packages
npm install

# Start the Vite development server
npm run dev
```

Open **`http://localhost:5173`** in your browser. All requests to `/api/v1/...` will proxy automatically to the local FastAPI backend.

---

## 📁 Repository Layout

- `backend/` — FastAPI application, SQLAlchemy models, AI pipeline engines, repositories, services, and test suite
- `frontend/` — React responsive student interface and analytics visualizations
- `ARCHITECTURE.md` — Detailed Clean Architecture documentation
- `SECURITY.md` — Security and authentication policies
=======
# skill_match_ai
>>>>>>> d9d3079b1d84cfdf4ad4bcbf4a244c67f1bca85d
