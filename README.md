# schule-infoportal-api

Unofficial API for accessing data from infoportal by art soft and more GmbH

## Features

This API provides the following endpoints to access infoportal data:

*   **Get All Substitutions**: Retrieve a complete list of all available substitutions available (`/substitutions`).
*   **Get Substitutions by Class**: Filter and retrieve substitutions specifically for a given class name (`/substitutions/{class_name}`).
*   **Get Substitutions by Teacher**: Find substitutions related to a specific absent teacher (`/substitutions/teacher/{teacher_name}`).
*   **Get Substitutions by Info**: Query substitutions based on specific information, such as "entfällt" (canceled) (`/substitutions/info/{info}`).
*   **Get All News Messages**: Fetch all news messages available in the infoportal (`/news`).
*   **Get Today's News Messages**: Retrieve news messages published for the current day (`/news/today`).
*   **Get News Messages by Date**: Access news messages for a specific date (`/news/date/{date}`).

All endpoints require basic HTTP authentication, configured via environment variables `API_USERNAME` and `API_PASSWORD`.

## Getting Started

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
