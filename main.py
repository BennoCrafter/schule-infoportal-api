from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
from src.news_message import NewsMessage
from src.substitution import Substitution
from src.parse import get_substitution_manager
import secrets
import os
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

app = FastAPI()
security = HTTPBasic()
substitution_manager = get_substitution_manager()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("API_USERNAME")
    correct_password = os.getenv("API_PASSWORD")

    if not correct_username or not correct_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error - credentials not set",
        )

    is_username_correct = secrets.compare_digest(credentials.username.encode("utf8"), correct_username.encode("utf8"))
    is_password_correct = secrets.compare_digest(credentials.password.encode("utf8"), correct_password.encode("utf8"))

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

@app.get("/auth/check", status_code=status.HTTP_200_OK)
async def check_auth(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Check if authentication credentials are valid
    """
    return {"message": "Authentication successful"}

@app.get("/substitutions/{class_name}", response_model=List[Substitution])
async def get_substitutions_for_class(class_name: str, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get all substitutions for a specific class.
    """
    substitutions = substitution_manager.get_substitutions_for_class(class_name)
    return substitutions


@app.get("/substitutions/teacher/{teacher_name}", response_model=List[Substitution])
async def get_substitutions_by_teacher(teacher_name: str, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get all substitutions for a specific teacher (absent teachers).
    """
    substitutions = substitution_manager.get_substitutions_with_property("absent_teacher", teacher_name)
    return substitutions


@app.get("/substitutions/info/{info}", response_model=List[Substitution])
async def get_substitutions_by_info(info: str, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get all substitutions by specific information (e.g., "entfällt" for canceled classes).
    """
    substitutions = substitution_manager.get_substitutions_with_property("info", info)
    return substitutions


@app.get("/substitutions", response_model=List[Substitution])
async def get_all_substitutions(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get all substitutions.
    """
    substitutions = substitution_manager.get_all_substitutions()
    return substitutions

@app.get("/news", response_model=List[NewsMessage])
async def get_all_news_messages(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get all news messages.
    """
    news_messages = substitution_manager.get_all_news_messages()
    return news_messages

@app.get("/news/today", response_model=List[NewsMessage])
async def get_today_news_messages(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get all news messages for today.
    """
    news_messages = substitution_manager.get_news_messages_for_today()
    return news_messages

@app.get("/news/date/{date}", response_model=List[NewsMessage])
async def get_news_messages_for_day(date: datetime.date, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get all news messages for a specific day.
    """
    news_messages = substitution_manager.get_news_messages_for_date(date)
    return news_messages
