import datetime
import logging
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.models.news_message_model import NewsMessage
from src.models.substitution_model import Substitution

logger = logging.getLogger(__name__)
load_dotenv()


class Parser:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        self._soup: Optional[BeautifulSoup] = None
        self._substitution_tables: Optional[list[BeautifulSoup]] = None
        self._news_table: Optional[BeautifulSoup] = None

    def fetch_html(self, username: str, password: str) -> Optional[str]:
        """
        Fetches the raw HTML content from the schule-infoportal.de/infoscreen/
        """
        url = (
            f"https://schule-infoportal.de/infoscreen/"
            f"?type=student&days={3}"
            f"&future=0&news={int(True)}"
            f"&ticker=anfang&absent=&absent2=1"
        )

        try:
            response = requests.get(url, auth=(username, password))  # type: ignore
            if response.status_code != 200:
                logger.error(f"Failed to fetch data: {response.status_code}")
                return None
            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def parse_tables(self, raw_html: str) -> bool:
        self._soup = BeautifulSoup(raw_html, "html.parser")

        main_table = self._soup.find("table", class_="main-table")
        if not main_table:
            logger.error("Main table not found")
            return False

        main_row_table = main_table.find("tr")
        if not main_row_table:
            logger.error("Main row not found")
            return False

        tables = main_row_table.find_all("td", recursive=False)
        logger.debug(f"Found {len(tables)} tables")

        if not tables:
            logger.error("No table cells found")
            return False

        # last table is the news table, all others are substitution tables
        self._substitution_tables = tables[:-1]  # type: ignore
        self._news_table = tables[-1]  # type: ignore

        return True

    @classmethod
    def run(cls, username: str, password: str) -> tuple["Parser", bool]:
        parser = cls(username=username, password=password)
        raw_html = parser.fetch_html(username=username, password=password)
        if raw_html is None:
            return parser, False

        return parser, parser.parse_tables(raw_html)

    def parse_substitutions(self) -> list[Substitution]:
        if not self._substitution_tables:  # if no raw substitution tables found
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

        inner_data: str | None = div.text.strip()

        if inner_data is None:
            logger.error("inner_data is None")
            return None

        match = re.search(
            r"Letzte Aktualisierung:\s*([\d]{2}\.[\d]{2}\.[\d]{4}\s[\d]{2}:[\d]{2}:[\d]{2})",
            inner_data,
        )

        if not match:
            logger.error("No valid last updated timestamp found")
            return None

        return datetime.datetime.strptime(match.group(1), "%d.%m.%Y %H:%M:%S")

    def _parse_substitution_table_date(self, date_str: str) -> datetime.date:
        """
        Parse date string from substitution table header. Example: "Mo., 22.09.2025 - KW 39"
        """
        date_str = date_str.split(",")[1].split("-")[0].strip()
        return datetime.datetime.strptime(date_str, "%d.%m.%Y").date()

    def _parse_substitution_table(self, table: BeautifulSoup) -> list[Substitution]:
        inner_table = table.find("div", class_="container daily_table")
        if not inner_table:
            logger.error("Substitution table not found")
            return []

        header = inner_table.find(
            "div", class_="daily_date_hdl week_odd"
        ) or inner_table.find("div", class_="daily_date_hdl week_even")

        if not header:
            logger.error("Date header not found")
            return []

        substitution_date = self._parse_substitution_table_date(header.text.strip())

        substitution_table = inner_table.find("table")
        if not substitution_table:
            logger.error("Real data table not found")
            return []

        rows = substitution_table.find_all("tr")
        logger.debug(f"Number of rows: {len(rows)}")

        substitutions: list[Substitution] = []
        previous_filled_cells_row: list[str] = []  # last row with non-empty cells
        for row in rows[1:]:  # skip header
            cells: list[str] = [cell.text.strip() for cell in row.find_all("td")]
            if len(cells) != 6:
                logger.info(f"Invalid row format: {cells}")
                continue

            if cells[0] == "" and previous_filled_cells_row:
                # handle case when class has more than one substitution entry for row where class cell is empty
                substitutions.extend(
                    self._convert_cells_to_substitutions(
                        [previous_filled_cells_row[0]] + cells[1:], substitution_date
                    )
                )

                continue

            substitutions.extend(
                self._convert_cells_to_substitutions(cells, substitution_date)
            )

            previous_filled_cells_row = cells

        return substitutions

    def _convert_cells_to_substitutions(
        self, cells: list[str], date: datetime.date
    ) -> list[Substitution]:
        class_name = cells[0]

        if not class_name.strip():
            return []

        if class_name[0].isdigit():  # 11b, 8a etc.
            match = re.match(r"(\d+)([a-zA-Z]+)", class_name)
            if not match:
                logger.warning(
                    f"No match found for class name: {class_name} parsing it into one substitution"
                )
                return [Substitution.from_array(cells, date)]

            substitutions = []
            for subclass in match.group(2):  # subclass = 'a', 'b', etc.
                substitutions.append(
                    Substitution.from_array_with_given_class_name(
                        cells, f"{match.group(1)}{subclass}", date
                    )
                )
            return substitutions
        else:  # Q12 or Q13
            return [Substitution.from_array(cells, date)]

    def _parse_news_table(self, news_table) -> list[NewsMessage]:
        """Parse a news table into a list of NewsMessage objects"""

        news = []
        if not news_table:
            logger.debug("No news table provided")
            return news

        day_news_blocks: list[BeautifulSoup] = news_table.find_all(
            "div", class_="news bb_border bb_bg_weiss"
        )
        for block in day_news_blocks:
            news_block_date = block.find("p", class_="news_headline_2")
            if not news_block_date:
                logger.error("News date missing")
                continue

            news_date: datetime.date = datetime.datetime.strptime(
                news_block_date.text.strip(), "%d.%m.%Y"
            ).date()

            text_element = block.find("span", class_="news_text")
            if not text_element:
                logger.error("News text missing")
                continue

            text = text_element.text.strip().replace("*", "").strip()
            for msg in text.split("\n\n"):
                news.append(NewsMessage(msg.strip(), news_date))

        return news
