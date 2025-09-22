# schule-infoportal-api

Unofficial API for accessing data from infoportal by art soft and more GmbH

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
