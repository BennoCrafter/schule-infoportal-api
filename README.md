# schule-infoportal-api

Unofficial API for accessing data from infoportal by art soft and more GmbH

# Features
---

### Auth Check


Checks if the provided credentials are valid.

| Method | URL |
|--------|-----|
| GET | /auth/check |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

---

### Get Substitutions


Get substitutions with optional filters:
- class_name: filter by class
- teacher_name: filter by absent teacher
- info: filter by info field (e.g., 'entfÃ¤llt')
- date: filter by exact date
- start_date + end_date: filter by date range

| Method | URL |
|--------|-----|
| GET | /substitutions |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| class_name | query | Filter by class name | Optional |
| teacher_name | query | Filter by absent teacher | Optional |
| info | query | Filter by info field (e.g., 'entfÃ¤llt') | Optional |
| date | query | Filter by specific date (YYYY-MM-DD) | Optional |
| start_date | query | Start of date range (YYYY-MM-DD) | Optional |
| end_date | query | End of date range (YYYY-MM-DD) | Optional |

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

---

### Get All News


Get all news messages.

| Method | URL |
|--------|-----|
| GET | /news |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

---

### Get Today News


Get today's news messages.

| Method | URL |
|--------|-----|
| GET | /news/today |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

---

### Get News For Date


Get news messages for a specific date.

| Method | URL |
|--------|-----|
| GET | /news/date/{date} |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| date | path |  | Required |

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

---

### Get Last Updated


Get the last updated time of Schule-Infoportal.

| Method | URL |
|--------|-----|
| GET | /last_updated |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|
| last_update | N/A |  |
| has_date | boolean |  |

---

### Get Internal Last Updated


Get the last updated time of the internal API.

| Method | URL |
|--------|-----|
| GET | /internal/last_updated |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|


---



# Getting Started

You can install and run this server using two methods: with Docker (recommended) or directly with Python and Uvicorn.

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
