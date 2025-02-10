import datetime as dt
import logging

import aiohttp
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://matchtv.ru/channel/matchtv/tvguide#content"
ITEM_CLASS = 'teleprogram-schedule__item'
TITLE_CLASS = 'teleprogram-item__title'
TIME_CLASS = 'teleprogram-item__time'
SCHEDULE_CLASS = 'schedule-line'


subscribed_users = set()
HTML_CACHE = None


async def fetch_html():
    global HTML_CACHE

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL) as response:
            response.raise_for_status()
            HTML_CACHE = await response.text()
    logger.info("HTML-страница обновлена")


async def get_schedule(sport_type: str):
    if HTML_CACHE is None:
        raise ValueError(
            "HTML-страница не загружена. Используйте команду /update."
        )
    soup = BeautifulSoup(HTML_CACHE, 'html.parser')
    schedule_items = soup.find_all('li', class_=ITEM_CLASS)
    schedule_lines = soup.find_all('div', class_=SCHEDULE_CLASS)

    current_time_utc = dt.datetime.now(dt.timezone.utc).timestamp()
    time_range = 3 * 3600
    min_time = current_time_utc - time_range
    max_time = current_time_utc + time_range

    schedule = []

    for item, schedule_line in zip(schedule_items, schedule_lines):
        title = item.find(
            'div',
            class_=TITLE_CLASS
        ).get_text(strip=True)
        start_time = int(schedule_line.get('data-schedule-line-start', 0))
        end_time = int(schedule_line.get('data-schedule-line-end', 0))
        if sport_type in title.lower() and min_time <= start_time <= max_time:
            formatted_start_time = dt.datetime.fromtimestamp(
                start_time
            ).strftime('%H:%M')
            formatted_end_time = dt.datetime.fromtimestamp(
                end_time
            ).strftime('%H:%M')
            schedule.append(
                f"{formatted_start_time} - {formatted_end_time} - {title}"
            )

    return schedule
