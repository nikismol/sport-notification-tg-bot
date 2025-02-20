import asyncio
import logging
import pytz

import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime as dt, timedelta

from database.engine import session_maker
from database.orm_query import orm_add_html, orm_get_html


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://matchtv.ru/channel/matchtv/tvguide#content"
ITEM_CLASS = 'teleprogram-schedule__item'
TITLE_CLASS = 'teleprogram-item__title'
SCHEDULE_CLASS = 'schedule-line'
subscribed_users = set()
MSK_TZ = pytz.timezone("Europe/Moscow")


async def fetch_html(db_session):

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL) as response:
            response.raise_for_status()
            data = await response.text()
            await orm_add_html(db_session, data)

    logger.info("HTML-страница обновлена")


async def fetch_html_auto():
    now = dt.now(MSK_TZ)

    next_midnight = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    ) + timedelta(
        days=1
    )

    seconds_until_midnight = (next_midnight - now).total_seconds()
    print(seconds_until_midnight)
    logger.info(
        f"Ожидание до {next_midnight.strftime('%Y-%m-%d %H:%M:%S')} МСК")

    await asyncio.sleep(seconds_until_midnight)
    while True:
        try:
            async with session_maker() as db_session:
                await fetch_html(db_session)
            logger.info("HTML-страница успешно обновлена "
                        f"в {dt.now(MSK_TZ)} МСК")
        except Exception as e:
            logger.error(f"Ошибка при обновлении HTML: {e}")

        await asyncio.sleep(7200)


async def get_schedule(sport_type: str):
    async with session_maker() as db_session:
        data = await orm_get_html(db_session)

    if data is None:
        raise ValueError(
            "Ошибка: data равно None. Надо загрузить страницу.")

    soup = BeautifulSoup(data, 'html.parser')
    li_items = soup.find_all('li', class_=ITEM_CLASS)

    current_time_msk = int(dt.now(MSK_TZ).timestamp())
    time_range = 3 * 3600
    min_time = current_time_msk - time_range
    max_time = current_time_msk + time_range

    schedule = []

    for li in li_items:
        title = li.find('div', class_=TITLE_CLASS).get_text(strip=True)
        info_time = li.find('div', class_=SCHEDULE_CLASS)
        if info_time:
            start_time = int(info_time.get('data-schedule-line-start'))
            end_time = int(info_time.get('data-schedule-line-end'))
            formatted_start_at = dt.fromtimestamp(start_time).strftime(
                '%H:%M')
            formatted_end_at = dt.fromtimestamp(end_time).strftime(
                '%H:%M')

            if sport_type in title.lower() and (
                    min_time <= start_time <= max_time
                    or
                    min_time <= end_time <= max_time
            ):

                schedule.append(
                    f"{formatted_start_at}-{formatted_end_at} - {title}"
                )

    return schedule
