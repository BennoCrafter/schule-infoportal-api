FROM python:3.13.3

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt


CMD ["fastapi", "run", "main.py", "--port", "8000"]
