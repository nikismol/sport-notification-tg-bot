import logging
import pytz

from bs4 import BeautifulSoup
from datetime import datetime as dt


from database.engine import session_maker
from database.orm_query import orm_get_html


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ITEM_CLASS = 'teleprogram-schedule__item'
TITLE_CLASS = 'teleprogram-item__title'
SCHEDULE_CLASS = 'schedule-line'
MSK_TZ = pytz.timezone("Europe/Moscow")


async def get_schedule(sport_type: str):
    async with session_maker() as db_session:
        data = await orm_get_html(db_session)

    if data is None:
        raise ValueError(
            "Ошибка: data равно None. Надо загрузить страницу."
        )

    soup = BeautifulSoup(data, 'html.parser')
    li_items = soup.find_all('li', class_=ITEM_CLASS)

    current_time_msk = int(dt.now(MSK_TZ).timestamp())
    min_time = current_time_msk - (1.5 * 3600)
    max_time = current_time_msk + (3 * 3600)

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

            if sport_type.lower() in title.lower() and (
                    min_time <= start_time <= max_time or
                    min_time <= end_time <= max_time
            ):

                schedule.append(
                    f"<u><i><b>{sport_type}</b></i></u>\n\n<strong>"
                    f"{formatted_start_at}-"
                    f"{formatted_end_at}</strong> - <i>{title}</i>\n"
                )
    return schedule
