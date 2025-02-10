import os
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from filters.chat_types import ChatTypeFilter
from handlers.user_handler import echo
from utils import fetch_html

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
router.message.filter(ChatTypeFilter('private'))

OWNER_ID = int(os.getenv("OWNER_ID"))


@router.message(Command("update"))
async def update_html(message: Message):
    if message.from_user.id != OWNER_ID:
        await echo(message)
        return

    await fetch_html()
    await message.answer(
        "HTML-страница обновлена! Теперь можно запрашивать расписание."
    )
