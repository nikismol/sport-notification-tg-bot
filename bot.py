import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeChat, BotCommandScopeAllPrivateChats
from dotenv import load_dotenv

from database.engine import create_db, session_maker

from common.bot_cmds_list import private, owner_commands
from handlers import admin_handler, user_handler
from middlewares.db import DataBaseMiddleware
from utils.auto_sent_notification import check_and_send_notification
from utils.update_program import auto_update_html

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))


async def on_startup():
    await create_db()


async def on_shutdown():
    print('bot shutdown')


async def main():
    bot = Bot(
        token=API_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(
        admin_handler.router,
        user_handler.router
    )
    dp.update.middleware(DataBaseMiddleware(session_pool=session_maker))
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
        auto_update_html()
    )
    asyncio.create_task(
        check_and_send_notification(bot)
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    logger.info("Bot is starting...")
    asyncio.run(main())
