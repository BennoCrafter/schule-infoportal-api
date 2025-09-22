from typing import Optional
from pydantic import BaseModel
import datetime

class NewsMessage(BaseModel):
    message: str
    date: datetime.date

    def __init__(self, message: str, date: datetime.date):
        super().__init__(message=message, date=date)

    def __str__(self):
        return f"{self.date}: {self.message}"
