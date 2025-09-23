import os
import re
import logging
import datetime
import requests
from typing import Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.models.substitution_model import Substitution
from src.models.news_message_model import NewsMessage
from src.models.config_model import Config

from src.utils.setup_logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()


class Parser:
    def __init__(self, config: Config):
        self.config = config
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")

        self._soup: Optional[BeautifulSoup] = None
        self._substitution_tables: Optional[list[BeautifulSoup]] = None
        self._news_table: Optional[BeautifulSoup] = None

        if self.username is None or self.password is None:
            logger.error("Missing USERNAME or PASSWORD in environment variables")
            raise ValueError("Missing USERNAME or PASSWORD in environment variables")

    def fetch_html(self) -> str:
        url = (
            f"https://schule-infoportal.de/infoscreen/"
            f"?type=student&days={self.config.days}"
            f"&future=0&news={int(self.config.show_news)}"
            f"&ticker=anfang&absent=&absent2=1"
        )

        try:
            response = requests.get(url, auth=(self.username, self.password)) # type: ignore
            if response.status_code != 200:
                logger.error(f"Failed to fetch data: {response.status_code}")
                raise requests.exceptions.RequestException(f"HTTP {response.status_code}")
            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def setup_parsing(self, raw_html: str):
        self._soup = BeautifulSoup(raw_html, "html.parser")

        main_table = self._soup.find("table", class_="main-table")
        if not main_table:
            logger.error("Main table not found")
            return None

        main_row = main_table.find("tr")
        table_cells = main_row.find_all("td", recursive=False)
        logger.debug(f"Found {len(table_cells)} tables")

        self._substitution_tables = table_cells[:-1] if self.config.show_news else table_cells
        self._news_table = table_cells[-1] if self.config.show_news else None

    def run_configuration(self):
        self.setup_parsing(self.fetch_html())

    def parse_substitutions(self) -> list[Substitution]:
        if not self._substitution_tables:
            return []

        substitutions = []
        for table in self._substitution_tables:
            substitutions.extend(self._parse_substitution_table(table))

        return substitutions

    def parse_news(self) -> list[NewsMessage]:
        return self._parse_news_table(self._news_table) if self._news_table else []

    def parse_last_updated(self) -> Optional[datetime.datetime]:
        if not self._soup:
            logger.error("Soup not initialized")
            return None

        div = self._soup.find("div", class_="copyright")
        if not div:
            logger.error("copyright_div not found")
            return None

        p = div.find("p")
        if not p:
            logger.error("Last updated element not found")
            return None

        match = re.search(
            r"Aktualisierung:\s*([\d]{2}\.[\d]{2}\.[\d]{4}\s[\d]{2}:[\d]{2}:[\d]{2})",
            p.text.strip(),
        )
        if not match:
            logger.error("No valid last updated timestamp found")
            return None

        return datetime.datetime.strptime(match.group(1), "%d.%m.%Y %H:%M:%S")

    def _parse_substitution_table_date(self, date_str: str) -> datetime.date:
        date_str = date_str.split(",")[1].split("-")[0].strip()
        return datetime.datetime.strptime(date_str, "%d.%m.%Y").date()

    def _parse_substitution_table(self, table) -> list[Substitution]:
        daily_table = table.find("div", class_="container daily_table")
        if not daily_table:
            logger.error("Substitution table not found")
            return []

        header = daily_table.find("div", class_="daily_date_hdl week_odd") \
                 or daily_table.find("div", class_="daily_date_hdl week_even")
        if not header:
            logger.error("Date header not found")
            return []

        substitution_date = self._parse_substitution_table_date(header.text.strip())

        rows = daily_table.find("table").find_all("tr") if daily_table.find("table") else []
        logger.debug(f"Number of rows: {len(rows)}")

        substitutions = []
        for row in rows[1:]:  # skip header
            cells = [cell.text.strip() for cell in row.find_all("td")]
            if len(cells) != 6:
                logger.error(f"Invalid row format: {cells}")
                continue
            substitutions.extend(self._convert_cells_to_substitutions(cells, substitution_date))

        return substitutions

    def _convert_cells_to_substitutions(self, cells: list[str], date: datetime.date) -> list[Substitution]:
        class_name = cells[0]

        if not class_name.strip():
            return []

        if class_name[0].isdigit():
            match = re.match(r"(\d+)([a-zA-Z]+)", class_name)
            if not match:
                logger.warning(f"No match found for class name: {class_name} parsing it into one substitution")
                return [Substitution.from_array(cells, date)]

            subs = []
            for cls_t in match.group(2):
                subs.append(Substitution.from_array_with_class_name(cells, f"{match.group(1)}{cls_t}", date))
            return subs
        else:
            # is e.g. Q12 or Q13
            return [Substitution.from_array(cells, date)]


    def _parse_news_table(self, news_table) -> list[NewsMessage]:
        news = []
        if not news_table:
            logger.debug("No news table provided")
            return news

        blocks = news_table.find_all("div", class_="news bb_border bb_bg_weiss")
        for block in blocks:
            date_el = block.find("p", class_="news_headline_2")
            if not date_el:
                logger.error("News date missing")
                continue

            news_date = datetime.datetime.strptime(date_el.text.strip(), "%d.%m.%Y").date()

            text_el = block.find("span", class_="news_text")
            if not text_el:
                logger.error("News text missing")
                continue

            text = text_el.text.strip().replace("*", "").strip()
            for msg in text.split("\n\n"):
                news.append(NewsMessage(msg.strip(), news_date))

        return news
