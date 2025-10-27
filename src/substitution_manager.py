import datetime
from typing import Optional

from src.models.last_update_model import LastUpdated
from src.models.substitution_model import Substitution
from src.models.news_message_model import NewsMessage
from src.models.config_model import Config

from src.parser import Parser
from src.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


class SubstitutionManager:
    def __init__(
        self,
        login_username: str,
        substitutions: list[Substitution],
        news: list[NewsMessage],
        last_info_portal_update: Optional[datetime.datetime] = None,
    ) -> None:
        self.login_username = login_username
        self.substitutions = substitutions
        self.news = news
        self.last_info_portal_update = last_info_portal_update
        self.last_internal_update: Optional[datetime.datetime] = None
        self.remove_duplicates()

    # --- Substitutions ---
    def get_all_substitutions(
        self,
        date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> list[Substitution]:
        """Return all substitutions, optionally filtered by date or date range."""
        return self._filter_and_sort_substitutions(
            self.substitutions, date=date, start_date=start_date, end_date=end_date
        )

    def get_substitutions_with_property(
        self,
        prop: str,
        value: str,
        date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> list[Substitution]:
        """Get substitutions where a property matches a value, optionally filtered by date/range."""
        filtered = [sub for sub in self.substitutions if getattr(sub, prop) == value]
        return self._filter_and_sort_substitutions(
            filtered, date=date, start_date=start_date, end_date=end_date
        )

    def get_substitutions_for_class(
        self,
        class_name: str,
        date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> list[Substitution]:
        """Convenience wrapper for filtering by class_name."""
        return self.get_substitutions_with_property(
            "class_name",
            class_name,
            date=date,
            start_date=start_date,
            end_date=end_date,
        )

    def _filter_and_sort_substitutions(
        self,
        substitutions: list[Substitution],
        date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> list[Substitution]:
        """Filter substitutions by exact date or date range and sort by date."""
        if date:
            substitutions = [sub for sub in substitutions if sub.date == date]
        elif start_date and end_date:
            substitutions = [
                sub for sub in substitutions if start_date <= sub.date <= end_date
            ]

        substitutions.sort(key=lambda sub: sub.date)
        return substitutions

    def remove_duplicates(self) -> None:
        self.substitutions = list(set(self.substitutions))

    # --- News ---
    def get_all_news_messages(self) -> list[NewsMessage]:
        return self._sort_news_messages_by_date(self.news)

    def get_news_messages_for_date(self, date: datetime.date) -> list[NewsMessage]:
        return self._sort_news_messages_by_date(
            [news for news in self.news if news.date == date]
        )

    def get_news_messages_for_today(self) -> list[NewsMessage]:
        return self.get_news_messages_for_date(datetime.date.today())

    def _sort_news_messages_by_date(
        self, news_messages: list[NewsMessage]
    ) -> list[NewsMessage]:
        return sorted(news_messages, key=lambda news: news.date)

    # --- Data management ---
    @staticmethod
    def _fetch_and_parse_data(
        config: Config, username: str, password: str
    ) -> Optional["SubstitutionManager"]:
        parser = Parser(config)
        success = parser.run(username, password)

        if not success:
            return None

        parsed_manager = SubstitutionManager(
            username,
            parser.parse_substitutions(),
            parser.parse_news(),
            parser.parse_last_updated(),
        )
        parsed_manager.last_internal_update = datetime.datetime.now()

        return parsed_manager

    @classmethod
    def init(
        cls, config: Config, username: str, password: str
    ) -> Optional["SubstitutionManager"]:
        return cls._fetch_and_parse_data(config, username, password)

    def update_data(self, config: Config, username: str, password: str) -> bool:
        fresh_manager = self._fetch_and_parse_data(config, username, password)
        if fresh_manager:
            self.__dict__.update(fresh_manager.__dict__)
            return True
        return False

    def check_updating_data(self) -> bool:
        last_update = self.get_last_internal_update().last_update
        if last_update is None:
            return False

        if last_update < datetime.datetime.now() - datetime.timedelta(minutes=5):
            # time for updating data
            return True

        return False

    # --- Metadata ---

    def get_last_internal_update(self) -> LastUpdated:
        return LastUpdated(
            last_update=self.last_internal_update,
            has_date=self.last_internal_update is not None,
        )

    def get_last_info_portal_update(self) -> LastUpdated:
        return LastUpdated(
            last_update=self.last_info_portal_update,
            has_date=self.last_info_portal_update is not None,
        )
