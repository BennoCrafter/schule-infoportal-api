import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import datetime
from src.substitution import Substitution
from src.news_message import NewsMessage
from src.substitution_manager import SubstitutionManager
import re
from typing import Optional
from src.config_model import Config


def get_last_updated_date(soup) -> Optional[datetime.datetime]:
    copyright_div = soup.find("div", class_="copyright")
    if not copyright_div:
        print("copyright_div not found")
        return None
    else:
        print("copyright_div found")

    last_updated_element = copyright_div.find('p')
    if last_updated_element:
        last_updated_text = last_updated_element.text.strip()
        match = re.search(r"Aktualisierung:\s*([\d]{2}\.[\d]{2}\.[\d]{4}\s[\d]{2}:[\d]{2}:[\d]{2})", last_updated_text)
        if not match:
            print("match not found")
            return None

        last_updated_date = datetime.datetime.strptime(match.group(1), '%d.%m.%Y %H:%M:%S')
        print(f"Last updated: {last_updated_date}")
    else:
        print("Last updated data not found")

def parse_substitution_table_date(date_str) -> datetime.date:
    date_str = date_str.split(",")[1].split("-")[0].strip()
    return datetime.datetime.strptime(date_str, "%d.%m.%Y").date()

def parse_substitution_table(substitution_table) -> list[Substitution]:
    daily_table = substitution_table.find("div", class_="container daily_table")
    if daily_table is None:
        print("Substitution table not found")
        return []

    date_header = daily_table.find("div", class_="daily_date_hdl week_odd") or daily_table.find("div", class_="daily_date_hdl week_even")
    if date_header is None:
        print("Date header not found")
        return []

    substitution_date = parse_substitution_table_date(date_header.text.strip())
    print(f"Substitution date: {substitution_date}")

    table_data = daily_table.find("table")
    if table_data is None:
        print("Table data not found")
        return []

    table_rows = table_data.find_all("tr")
    print(len(table_rows))

    substitutions = []
    # first cell is header. skip it
    for row in table_rows[1:]:
        cells = row.find_all("td")
        cells = [cell.text.strip() for cell in cells]
        if len(cells) != 6:
            print(f"Wrong data. Cells do not match expected format: {cells}  ({len(cells)} != 6)")
            continue

        substitutions.append(Substitution.from_array(cells, substitution_date))

    return substitutions

def parse_news_table(news_table) -> list[NewsMessage]:
    news: list[NewsMessage] = []

    news_date_blocks = news_table.find_all("div", class_="news bb_border bb_bg_weiss")
    for news_date_block in news_date_blocks:
        news_date_element = news_date_block.find("p", class_="news_headline_2")
        if news_date_element is None:
            print("News date element not found")
            continue

        news_date: datetime.date = datetime.datetime.strptime(news_date_element.text.strip(), "%d.%m.%Y").date()
        news_text_element = news_date_block.find("span", class_="news_text")
        if news_text_element is None:
            print("News text element not found")
            continue
        news_text: str = news_text_element.text.strip().replace("*", "").strip()

        for news_message in news_text.split("\n\n"):
            news.append(NewsMessage(str(news_message), news_date))

    return news

def parse_html(raw_html_content: str, config: Config) -> Optional[SubstitutionManager]:
    soup = BeautifulSoup(raw_html_content, 'html.parser')
    last_update: Optional[datetime.datetime] = get_last_updated_date(soup)
    substitutions: list[Substitution] = []
    news: list[NewsMessage] = []

    main_table = soup.find("table", class_="main-table")

    if not main_table:
        print("Main table not found")
        return None
    else:
        print("Main table found")

    main_table_row = main_table.find('tr')

    main_table_tables = main_table_row.find_all('td', recursive=False)
    print(len(main_table_tables))

    substitution_tables = main_table_tables[0:len(main_table_tables)-1 if config.show_news else len(main_table_tables)]

    news_table = main_table_tables[-1] if config.show_news else None
    if news_table:
        print("News table found")
        news = parse_news_table(news_table)
        for news_message in news:
            print(news_message)
    else:
        print("News table not found")

    for substitution_table in substitution_tables:
        substitutions.extend(parse_substitution_table(substitution_table))

    return SubstitutionManager(substitutions, news)


def get_substitution_manager(config: Config = Config()) -> SubstitutionManager:
    """
    Initialize and return the SubstitutionManager.
    """
    load_dotenv()

    url = f"https://schule-infoportal.de/infoscreen/?type=student&days={config.days}&future=0&news={int(config.show_news)}&ticker=anfang&absent=&absent2=1"
    username = str(os.getenv('USERNAME'))
    password = str(os.getenv('PASSWORD'))

    if not username or not password:
        print("Missing username or password in environment variables")
        raise ValueError("Missing username or password in environment variables")

    try:
        response = requests.get(url, auth=(username, password))

        if response.status_code != 200:
            print()
            raise requests.exceptions.RequestException("Failed to get substitution data: " + str(response.status_code))

        sub_manager = parse_html(response.text, config)
        if sub_manager is None:
            print("Failed to parse substitution data")
            raise ValueError("Failed to parse substitution data")
        return sub_manager

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        raise e
    except Exception as e:
        print("An unexpected error occurred:", e)
        raise e
