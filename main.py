from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List

from starlette.types import Lifespan
from src.models.config_model import Config
from src.models.news_message_model import NewsMessage
from src.models.last_update_model import LastUpdated
from src.models.substitution_model import Substitution
import secrets
import os
from dotenv import load_dotenv
import datetime
import asyncio
from src.utils.setup_logger import setup_logger
from contextlib import asynccontextmanager
from src.substitution_manager import SubstitutionManager

# Load environment variables
load_dotenv()


logger = setup_logger(__name__)

async def refresh_substitution_manager_task():
    while True:
        await asyncio.sleep(config.refresh_interval * 60)
        logger.info(f"[{datetime.datetime.now()}] Attempting to refresh substitution data...")
        substitution_manager.update_data(config)
        logger.info(f"[{datetime.datetime.now()}] Substitution data finished updating.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(refresh_substitution_manager_task())
    logger.info("Substitution data refresh task scheduled.")
    yield

config = Config()
app = FastAPI(lifespan=lifespan)
security = HTTPBasic()
substitution_manager: SubstitutionManager = SubstitutionManager.init(config)


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

@app.get("/last_updated", response_model=LastUpdated)
async def get_last_updated(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get the last updated time of schule-infoportal.
    """
    return substitution_manager.get_last_info_portal_update()

@app.get("/internal/last_updated")
async def get_last_internal_updated(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Get the last updated time of the internal api when last time data was fetched.
    """
    return substitution_manager.get_last_internal_update()
