import datetime

from pydantic import BaseModel


class RawNewsMessage(BaseModel):
    raw_text: str
    date: datetime.date

    def __init__(self, raw_text: str, date: datetime.date):
        super().__init__(raw_text=raw_text, date=date)

    def __str__(self):
        return f"{self.date}: {self.raw_text}"
