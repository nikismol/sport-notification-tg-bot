import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import (TelegramForbiddenError, TelegramNotFound,
                                TelegramRetryAfter)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommandScopeChat, BotCommandScopeAllPrivateChats
from dotenv import load_dotenv

from common.bot_cmds_list import private, owner_commands
from handlers import admin_handler, user_handler
from utils import fetch_html_auto, get_schedule, subscribed_users

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

storage = MemoryStorage()


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
                to_remove = set()

                for user_id in subscribed_users:
                    try:
                        await bot.send_message(user_id, message)
                    except TelegramForbiddenError:
                        logger.warning(
                            f"❌ Бот заблокирован пользователем {user_id}. Удаляем из подписчиков.")
                        to_remove.add(user_id)
                    except TelegramNotFound:
                        logger.warning(
                            f"❌ Чат {user_id} не найден. Удаляем из подписчиков.")
                        to_remove.add(user_id)
                    except TelegramRetryAfter as e:
                        logger.warning(
                            f"⚠️ Превышен лимит отправки сообщений. Ждём {e.timeout} секунд...")
                        await asyncio.sleep(e.timeout)
                    except Exception as e:
                        logger.error(
                            f"Error sending message to {user_id}: {e}"
                        )
        except Exception as e:
            logger.error(f"Error while checking schedule: {e}")
        await asyncio.sleep(10800)


async def main():
    bot = Bot(
        token=API_TOKEN
    )
    dp = Dispatcher(
        storage=storage
    )
    dp.include_routers(
        admin_handler.router,
        user_handler.router
    )
    await bot.delete_webhook(
        drop_pending_updates=True
    )
    await bot.delete_my_commands(
        scope=BotCommandScopeAllPrivateChats()
    )
    await bot.set_my_commands(
        commands=private,
        scope=BotCommandScopeAllPrivateChats()
    )
    await bot.set_my_commands(
        commands=owner_commands,
        scope=BotCommandScopeChat(chat_id=OWNER_ID)
    )
    asyncio.create_task(
        fetch_html_auto()
    )
    asyncio.create_task(
        check_schedule_and_notify(bot)
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    logger.info("Bot is starting...")
    asyncio.run(main())
