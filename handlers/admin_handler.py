import os
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter
from handlers.user_handler import echo
from utils.update_program import manual_update_html

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
router.message.filter(ChatTypeFilter('private'))

OWNER_ID = int(os.getenv("OWNER_ID"))


@router.message(Command("update"))
async def update_html(message: Message, session: AsyncSession):
    if message.from_user.id != OWNER_ID:
        await echo(message)
        return
    try:
        await manual_update_html(db_session=session)
        await message.answer("HTML обновлен успешно!")
    except Exception as e:
        await message.answer(f"Ошибка при обновлении: {e}")
