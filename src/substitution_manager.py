import datetime
from src.substitution import Substitution
from src.news_message import NewsMessage


class SubstitutionManager:
    def __init__(self, substitutions: list[Substitution], news: list[NewsMessage]) -> None:
        self.substitutions = substitutions
        self.news = news
        self.remove_duplicates()

    def get_substitutions_with_property(self, prop: str, value: str) -> list[Substitution]:
            """Get all substitutions with a specific property."""
            return [sub for sub in self.substitutions if getattr(sub, prop) == value]

    def get_substitutions_for_class(self, class_name: str) -> list[Substitution]:
        return self.get_substitutions_with_property("class_name", class_name)

    def get_all_substitutions(self) -> list[Substitution]:
        return self.substitutions

    def remove_duplicates(self) -> None:
        self.substitutions = list(set(self.substitutions))

    def get_all_news_messages(self) -> list[NewsMessage]:
        return self._sort_news_messages_by_date(self.news)

    def get_news_messages_for_date(self, date: datetime.date) -> list[NewsMessage]:
        return self._sort_news_messages_by_date([news for news in self.news if news.date == date])

    def get_news_messages_for_today(self) -> list[NewsMessage]:
        return self._sort_news_messages_by_date(self.get_news_messages_for_date(datetime.date.today()))

    def _sort_news_messages_by_date(self, news_messages: list[NewsMessage]) -> list[NewsMessage]:
        news_messages.sort(key=lambda news: news.date)
        return news_messages
