# schule-infoportal-api

Unofficial API for accessing data from infoportal by art soft and more GmbH

# Features
---

## 🔑 Authentication

### `GET /auth/check`

Checks if the provided credentials are valid.

**Auth Required:** ✅  
**Response:**
```json
{
  "message": "Authentication successful"
}
```

**Error Codes:**
- `401 Unauthorized`: Invalid credentials
- `500 Internal Server Error`: Server credentials not set

---

## 📅 Substitutions

### `GET /substitutions`

Retrieve substitutions with optional filters.

**Auth Required:** ✅  

**Query Parameters:**
- `class_name` (string, optional) → Filter by class name  
- `teacher_name` (string, optional) → Filter by absent teacher  
- `info` (string, optional) → Filter by info field (e.g., `"entfällt"`)  
- `date` (YYYY-MM-DD, optional) → Filter by exact date  
- `start_date` (YYYY-MM-DD, optional) → Start of date range  
- `end_date` (YYYY-MM-DD, optional) → End of date range  

**Response Model:** `List[Substitution]`

---

## 📰 News

### `GET /news`

Retrieve all news messages.

**Auth Required:** ✅  
**Response Model:** `List[NewsMessage]`

---

### `GET /news/today`

Retrieve today’s news messages.

**Auth Required:** ✅  
**Response Model:** `List[NewsMessage]`

---

### `GET /news/date/{date}`

Retrieve news messages for a specific date.

**Auth Required:** ✅  

**Path Parameter:**
- `date` (YYYY-MM-DD) → Specific date

**Response Model:** `List[NewsMessage]`

---

## 📊 Metadata

### `GET /last_updated`

Retrieve the last updated time of the Schule-Infoportal.

**Auth Required:** ✅  
**Response Model:** `LastUpdated`

---

### `GET /internal/last_updated`

Retrieve the last updated time of the **internal API**.

**Auth Required:** ✅  
**Response Model:** `LastUpdated`

---

## ⚙️ Background Tasks

- The API automatically refreshes substitution data every **`config.refresh_interval` minutes**.
- Refresh logs are stored via `setup_logger`.

---

All endpoints require basic HTTP authentication, configured via environment variables `API_USERNAME` and `API_PASSWORD`.

# Getting Started

You can install and run this application using two methods: with Docker (recommended) or directly with Python and Uvicorn.

### Option A: Using Docker (Recommended)

This method provides a consistent environment and simplifies setup.

#### 1. Build Docker Image

From the root of the project directory:

```bash
docker-compose up -d --build
```

### Option B: Using Python and Uvicorn

This method requires a local Python environment.

#### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate # On Windows: .\venv\Scripts\activate
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Run the Application

Once dependencies are installed, you can run the application locally:

```bash
uvicorn main:app --reload
```
This will start the Uvicorn server, typically accessible at `http://127.0.0.1:8000`. The `--reload` flag enables auto-reloading on code changes, which is useful for development.
