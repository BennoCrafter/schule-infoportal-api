from pydantic import BaseModel

class Config(BaseModel):
    days: int = 3
    show_news: bool = True
    refresh_interval: int = 5 # in minutes
