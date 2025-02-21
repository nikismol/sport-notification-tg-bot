import asyncio
import logging
import pytz

import aiohttp
from datetime import datetime as dt, timedelta

from database.engine import session_maker
from database.orm_query import orm_add_html


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://matchtv.ru/channel/matchtv/tvguide#content"
MSK_TZ = pytz.timezone("Europe/Moscow")


async def manual_update_html(db_session):

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL) as response:
            response.raise_for_status()
            data = await response.text()
            await orm_add_html(db_session, data)

    logger.info("HTML-страница обновлена")


async def auto_update_html():
    while True:
        now = dt.now(MSK_TZ)
        next_midnight = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) + timedelta(days=1)
        seconds_until_midnight = (next_midnight - now).total_seconds()
        logger.info(
            f"Секунд до обновления {seconds_until_midnight}")
        print(seconds_until_midnight)
        logger.info(
            f"Ожидание до {next_midnight.strftime('%Y-%m-%d %H:%M:%S')} МСК")

        await asyncio.sleep(seconds_until_midnight)
        while True:
            try:
                async with session_maker() as db_session:
                    await manual_update_html(db_session)
                logger.info(
                    "HTML-страница успешно обновлена "
                    f"в {dt.now(MSK_TZ)} МСК"
                    )
                await asyncio.sleep(7200)
            except Exception as e:
                logger.error(f"Ошибка при обновлении HTML: {e}")
                await asyncio.sleep(300)
