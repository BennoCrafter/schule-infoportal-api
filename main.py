from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
import datetime
from typing import Annotated

from src.models.config_model import Config
from src.models.news_message_model import NewsMessage
from src.models.last_update_model import LastUpdated
from src.models.substitution_model import Substitution
from src.substitution_updater import SubstitutionUpdater
from src.utils.setup_logger import setup_logger


# --- Setup ---
logger = setup_logger(__name__)

config = Config()
app = FastAPI(title="Schule-Infoportal API", version="1.0.0")
security = HTTPBasic()
substitution_updater: SubstitutionUpdater = SubstitutionUpdater()


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("public/favicon.ico")


@app.get("/apple-touch-icon.png", include_in_schema=False)
async def apple_touch_icon():
    return FileResponse("public/apple-touch-icon.png")


@app.get("/auth/check")
async def auth_check(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """Checks if the provided credentials are valid."""
    substitution_manager = substitution_updater.get_substitution_manager(
        config, credentials.username, credentials.password
    )
    if substitution_manager is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Authentication successful"}


# --- Substitutions ---


@app.get("/substitutions", response_model=List[Substitution])
async def get_substitutions(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    class_name: Optional[str] = Query(None, description="Filter by class name"),
    teacher_name: Optional[str] = Query(None, description="Filter by absent teacher"),
    info: Optional[str] = Query(
        None, description="Filter by info field (e.g., 'entfällt')"
    ),
    date: Optional[datetime.date] = Query(
        None, description="Filter by specific date (YYYY-MM-DD)"
    ),
    start_date: Optional[datetime.date] = Query(
        None, description="Start of date range (YYYY-MM-DD)"
    ),
    end_date: Optional[datetime.date] = Query(
        None, description="End of date range (YYYY-MM-DD)"
    ),
):
    """
    Get substitutions with optional filters:
    - class_name: filter by class
    - teacher_name: filter by absent teacher
    - info: filter by info field (e.g., 'entfällt')
    - date: filter by exact date
    - start_date + end_date: filter by date range
    """

    substitution_manager = substitution_updater.get_substitution_manager(
        config, credentials.username, credentials.password
    )
    if substitution_manager is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if class_name:
        return substitution_manager.get_substitutions_for_class(
            class_name, date=date, start_date=start_date, end_date=end_date
        )

    if teacher_name:
        return substitution_manager.get_substitutions_with_property(
            "absent_teacher",
            teacher_name,
            date=date,
            start_date=start_date,
            end_date=end_date,
        )

    if info:
        return substitution_manager.get_substitutions_with_property(
            "info", info, date=date, start_date=start_date, end_date=end_date
        )

    return substitution_manager.get_all_substitutions(
        date=date, start_date=start_date, end_date=end_date
    )


# --- News ---
@app.get("/news", response_model=List[NewsMessage])
async def get_all_news(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """Get all news messages."""
    substitution_manager = substitution_updater.get_substitution_manager(
        config, credentials.username, credentials.password
    )
    if substitution_manager is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return substitution_manager.get_all_news_messages()


@app.get("/news/today", response_model=List[NewsMessage])
async def get_today_news(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Get today's news messages."""
    substitution_manager = substitution_updater.get_substitution_manager(
        config, credentials.username, credentials.password
    )
    if substitution_manager is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return substitution_manager.get_news_messages_for_today()


@app.get("/news/date/{date}", response_model=List[NewsMessage])
async def get_news_for_date(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    date: datetime.date,
):
    """Get news messages for a specific date."""
    substitution_manager = substitution_updater.get_substitution_manager(
        config, credentials.username, credentials.password
    )
    if substitution_manager is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return substitution_manager.get_news_messages_for_date(date)


# --- Metadata ---
@app.get("/last_updated", response_model=LastUpdated)
async def get_last_updated(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Get the last updated time of Schule-Infoportal."""
    substitution_manager = substitution_updater.get_substitution_manager(
        config, credentials.username, credentials.password
    )
    if substitution_manager is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return substitution_manager.get_last_info_portal_update()


@app.get("/internal/last_updated")
async def get_internal_last_updated(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Get the last updated time of the internal API."""
    substitution_manager = substitution_updater.get_substitution_manager(
        config, credentials.username, credentials.password
    )
    if substitution_manager is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return substitution_manager.get_last_internal_update()
