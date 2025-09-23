from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
from starlette.types import Lifespan
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import secrets
import os
import datetime
import asyncio

from src.models.config_model import Config
from src.models.news_message_model import NewsMessage
from src.models.last_update_model import LastUpdated
from src.models.substitution_model import Substitution
from src.substitution_manager import SubstitutionManager
from src.utils.setup_logger import setup_logger


# --- Setup ---
load_dotenv()
logger = setup_logger(__name__)

config = Config()
app = FastAPI(title="Substitution API", version="1.0.0")
security = HTTPBasic()
substitution_manager: SubstitutionManager = SubstitutionManager.init(config)


# --- Background refresh task ---
async def refresh_substitution_manager_task():
    while True:
        await asyncio.sleep(config.refresh_interval * 60)
        logger.info(f"[{datetime.datetime.now()}] Refreshing substitution data...")
        substitution_manager.update_data(config)
        logger.info(f"[{datetime.datetime.now()}] Substitution data updated.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(refresh_substitution_manager_task())
    logger.info("Substitution refresh task scheduled.")
    yield
    task.cancel()
    logger.info("Substitution refresh task cancelled.")


app.router.lifespan_context = lifespan


# --- Authentication ---
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if os.getenv("API_USERNAME") is None and os.getenv("API_PASSWORD") is None:
        correct_username = os.getenv("USERNAME")
        correct_password = os.getenv("PASSWORD")
    else:
        correct_username = os.getenv("API_USERNAME")
        correct_password = os.getenv("API_PASSWORD")

    if not correct_username or not correct_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: credentials not set",
        )

    if not (
        secrets.compare_digest(credentials.username, correct_username)
        and secrets.compare_digest(credentials.password, correct_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials


# --- Auth ---
@app.get("/auth/check", status_code=status.HTTP_200_OK)
async def check_auth(_: HTTPBasicCredentials = Depends(verify_credentials)):
    """Check if authentication credentials are valid."""
    return {"message": "Authentication successful"}


# --- Substitutions ---
@app.get("/substitutions", response_model=List[Substitution])
async def get_substitutions(
    class_name: Optional[str] = Query(None, description="Filter by class name"),
    teacher_name: Optional[str] = Query(None, description="Filter by absent teacher"),
    info: Optional[str] = Query(None, description="Filter by info field (e.g., 'entfällt')"),
    date: Optional[datetime.date] = Query(None, description="Filter by specific date (YYYY-MM-DD)"),
    start_date: Optional[datetime.date] = Query(None, description="Start of date range (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="End of date range (YYYY-MM-DD)"),
    _: HTTPBasicCredentials = Depends(verify_credentials),
):
    """
    Get substitutions with optional filters:
    - class_name: filter by class
    - teacher_name: filter by absent teacher
    - info: filter by info field (e.g., 'entfällt')
    - date: filter by exact date
    - start_date + end_date: filter by date range
    """

    if class_name:
        return substitution_manager.get_substitutions_for_class(
            class_name, date=date, start_date=start_date, end_date=end_date
        )

    if teacher_name:
        return substitution_manager.get_substitutions_with_property(
            "absent_teacher", teacher_name,
            date=date, start_date=start_date, end_date=end_date
        )

    if info:
        return substitution_manager.get_substitutions_with_property(
            "info", info,
            date=date, start_date=start_date, end_date=end_date
        )

    return substitution_manager.get_all_substitutions(
        date=date, start_date=start_date, end_date=end_date
    )

# --- News ---
@app.get("/news", response_model=List[NewsMessage])
async def get_all_news(
    _: HTTPBasicCredentials = Depends(verify_credentials),
):
    """Get all news messages."""
    return substitution_manager.get_all_news_messages()


@app.get("/news/today", response_model=List[NewsMessage])
async def get_today_news(
    _: HTTPBasicCredentials = Depends(verify_credentials),
):
    """Get today's news messages."""
    return substitution_manager.get_news_messages_for_today()


@app.get("/news/date/{date}", response_model=List[NewsMessage])
async def get_news_for_date(
    date: datetime.date,
    _: HTTPBasicCredentials = Depends(verify_credentials),
):
    """Get news messages for a specific date."""
    return substitution_manager.get_news_messages_for_date(date)


# --- Metadata ---
@app.get("/last_updated", response_model=LastUpdated)
async def get_last_updated(
    _: HTTPBasicCredentials = Depends(verify_credentials),
):
    """Get the last updated time of Schule-Infoportal."""
    return substitution_manager.get_last_info_portal_update()


@app.get("/internal/last_updated")
async def get_internal_last_updated(
    _: HTTPBasicCredentials = Depends(verify_credentials),
):
    """Get the last updated time of the internal API."""
    return substitution_manager.get_last_internal_update()
