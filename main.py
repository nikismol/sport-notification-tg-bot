import asyncio
import os
import datetime as dt
import logging
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")

storage = MemoryStorage()
router = Router()
dp = Dispatcher(storage=storage)

BASE_URL = "https://matchtv.ru/channel/matchtv/tvguide#content"
ITEM_CLASS = 'teleprogram-schedule__item'
TITLE_CLASS = 'teleprogram-item__title'
TIME_CLASS = 'teleprogram-item__time'
SCHEDULE_CLASS = 'schedule-line'


subscribed_users = set()


async def get_schedule(sport_type: str):
    url = BASE_URL
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            html = await response.text()

    soup = BeautifulSoup(html, 'html.parser')
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
            class_='teleprogram-item__title'
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


async def check_schedule_and_notify(bot: Bot):
    while True:
        try:
            biathlon_schedule = await get_schedule('биатлон')
            football_schedule = await get_schedule('футбол')
            billiards_schedule = await get_schedule('бильярд')

            message = ""

            if biathlon_schedule:
                message += f"Биатлон:\n{'\n'.join(biathlon_schedule)}\n\n"
            if football_schedule:
                message += f"Футбол:\n{'\n'.join(football_schedule)}\n\n"
            if billiards_schedule:
                message += f"Бильярд:\n{'\n'.join(billiards_schedule)}\n\n"

            if message:
                for user_id in subscribed_users:
                    try:
                        await bot.send_message(user_id, message)
                    except Exception as e:
                        logger.error(
                            f"Error sending message to {user_id}: {e}"
                        )
        except Exception as e:
            logger.error(f"Error while checking schedule: {e}")
        await asyncio.sleep(10800)


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    # Добавляем пользователя в список подписчиков, если его там нет
    if user_id not in subscribed_users:
        subscribed_users.add(user_id)
        logger.info(f"User {user_id} subscribed.")

    await message.answer(
        "Привет! Я могу отправить тебе расписание биатлона или футбола."
        "\nНапиши /biathlon, чтобы узнать расписание биатлона."
        "\nНапиши /football, чтобы узнать расписание футбола."
        "\nНапиши /billiards, чтобы узнать расписание бильярда."
    )


@dp.message(Command("biathlon"))
async def send_biathlon_schedule(message: types.Message):
    schedule = await get_schedule('биатлон')
    response = (
        "\n".join(schedule) if schedule
        else "На данный момент биатлон не запланирован."
    )
    await message.answer(response, parse_mode='Markdown')


@dp.message(Command("billiards"))
async def send_billiards_schedule(message: types.Message):
    schedule = await get_schedule('бильярд')
    response = (
        "\n".join(schedule) if schedule
        else "На данный момент бильярд не запланирован."
    )
    await message.answer(response, parse_mode='Markdown')


@dp.message(Command("football"))
async def send_football_schedule(message: types.Message):
    schedule = await get_schedule('футбол')
    response = (
        "\n".join(schedule) if schedule
        else "На данный момент футбол не запланирован."
    )
    await message.answer(response, parse_mode='Markdown')


@dp.message()
async def echo(message: types.Message):
    await message.answer(
        "Для получения расписания биатлона напиши /biathlon. "
        "Для получения расписания футбола напиши /football. "
        "Для получения расписания бильярда напиши /billiards"
    )


async def main():
    bot = Bot(token=API_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(check_schedule_and_notify(bot))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logger.info("Bot is starting...")
    asyncio.run(main())
