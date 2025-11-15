from pydantic import BaseModel


class APIConfig(BaseModel):
    get_substitutions: bool = True
    get_news: bool = True
