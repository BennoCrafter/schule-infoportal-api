from typing import Optional
from pydantic import BaseModel
import datetime

class LastUpdated(BaseModel):
    last_update: Optional[datetime.datetime]
    has_date: bool

    def __init__(self, last_update: Optional[datetime.datetime], has_date: bool):
        super().__init__(last_update=last_update, has_date=has_date)

    def __str__(self):
        return f"{self.last_update}: {self.has_date}"
