# Attendance Management API

Production-ready FastAPI backend for managing student attendance, backed by **MongoDB Atlas** and deployable on **Render**.

## Features

- Async FastAPI endpoints with Swagger docs at `/docs`
- MongoDB Atlas via Motor (async driver)
- Excel/CSV bulk upload with pandas validation
- Upload history tracking in MongoDB
- CORS, structured logging, and global exception handling
- Pydantic v2 request/response validation
- Render-ready deployment configuration

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| Database | MongoDB Atlas |
| Driver | Motor (AsyncIO) |
| Validation | Pydantic v2 |
| File parsing | Pandas + OpenPyXL |
| Hosting | Render Web Service |

## Project Structure

```
app/
├── api/              # Route handlers
├── database/         # MongoDB connection (mongodb.py)
├── schemas/          # Pydantic models
├── services/         # Business logic
├── utils/            # Logging, validators, helpers
├── uploads/          # Uploaded file storage
└── main.py           # Application entry point
render.yaml           # Render deployment blueprint
Procfile              # Process definition
runtime.txt           # Python version for Render
requirements.txt
```

## MongoDB Collections

Database: `attendance_portal`

| Collection | Purpose |
|------------|---------|
| `students` | Student profiles with embedded subject attendance |
| `attendance_uploads` | Upload history (filename, counts, timestamp) |
| `announcements` | Portal announcements |
| `settings` | Global settings (minimum attendance, semester, academic year) |

### Student document shape

```json
{
  "register_number": "21CS001",
  "name": "Aarav Sharma",
  "department": "Computer Science & Engineering",
  "year": "III",
  "section": "A",
  "semester": "6",
  "attendance": [
    {
      "subject_code": "CS3401",
      "subject_name": "Algorithms",
      "classes_conducted": 45,
      "classes_attended": 42,
      "percentage": 93.3
    }
  ],
  "overall_percentage": 88.5,
  "last_updated": "2026-07-05T08:33:06.938626Z"
}
```

## Requirements

- Python 3.12+ (recommended for Render)
- MongoDB Atlas cluster (or local MongoDB for development)
- pip

---

## Local Setup

### 1. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
cd c:\Users\ABI\Desktop\attendance
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
copy .env.example .env
```

Edit `.env`:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
DATABASE_NAME=attendance_portal
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO
```

### 4. Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API base: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

---

## MongoDB Atlas Setup

1. Sign in at [mongodb.com/atlas](https://www.mongodb.com/atlas) and create a free cluster.
2. Create a database user with read/write access.
3. Under **Network Access**, add your IP (or `0.0.0.0/0` for Render).
4. Click **Connect → Drivers** and copy the connection string.
5. Replace `<username>` and `<password>` in the URI and set it as `MONGODB_URI`.

Example:

```env
MONGODB_URI=mongodb+srv://admin:YourPassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

Indexes on `register_number` and `attendance.subject_code` are created automatically on startup.

---

## Render Deployment

### Option A: Blueprint (render.yaml)

1. Push this repo to GitHub.
2. In Render, click **New → Blueprint** and connect the repository.
3. Set `MONGODB_URI` and `CORS_ORIGINS` as secret environment variables.
4. Deploy.

### Option B: Manual Web Service

1. **New → Web Service** → connect your repo.
2. Configure:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables:

| Key | Value |
|-----|-------|
| `MONGODB_URI` | Your Atlas connection string |
| `DATABASE_NAME` | `attendance_portal` |
| `CORS_ORIGINS` | Your frontend URL (e.g. `https://your-app.onrender.com`) |
| `LOG_LEVEL` | `INFO` |

4. Deploy and verify `https://<your-service>.onrender.com/health`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/student/{register_number}` | Student details with overall and subject-wise attendance |
| GET | `/students` | List all students |
| GET | `/statistics` | Attendance statistics, rankings, and total students |
| POST | `/upload` | Upload Excel/CSV attendance file |
| GET | `/health` | Health check with database connectivity status |

### Health response

```json
{
  "status": "ok",
  "database": "connected"
}
```

### Upload response

```json
{
  "updated": 5,
  "added": 3,
  "failed": 1,
  "errors": ["Row 4: Classes attended cannot exceed classes conducted."]
}
```

### Statistics response

```json
{
  "average_attendance": 87.9,
  "students_below_75": [],
  "top_10_attendance": [...],
  "lowest_attendance": [...],
  "total_students": 120
}
```

---

## Upload File Format

Supported formats: `.csv`, `.xlsx`, `.xls`

| Column | Description |
|--------|-------------|
| Register Number | Unique student ID (required) |
| Student Name | Full name |
| Department | Department name |
| Year | Academic year |
| Section | Section |
| Semester | Semester |
| Subject Code | Subject code |
| Subject Name | Subject name |
| Classes Conducted | Total classes held |
| Classes Attended | Classes attended |

The backend automatically calculates percentage, overall attendance, and `last_updated`. Duplicate subjects for the same student are updated in place.

---

## Frontend Integration

```env
VITE_API_BASE=https://your-api.onrender.com
```

> The frontend calls `GET /students/{register_number}` but this API exposes `GET /student/{register_number}`. Update `frontend/src/lib/api.ts` accordingly.

---

## Example Requests

```bash
curl https://your-api.onrender.com/health
curl https://your-api.onrender.com/student/21CS001
curl -X POST https://your-api.onrender.com/upload -F "file=@sample_attendance.csv"
curl https://your-api.onrender.com/statistics
```

---

## Security

- Upload file type and size validation
- Register number format validation
- Input sanitization on text fields
- Unique index on `register_number` prevents duplicates
- CORS restricted to configured origins
"# attendance-system" 
