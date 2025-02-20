import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_user, orm_delete_user, orm_get_user
from filters.chat_types import ChatTypeFilter
from utils import get_schedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()
router.message.filter(ChatTypeFilter('private'))


@router.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Я могу отправить тебе расписание биатлона или футбола."
        "\nНапиши /biathlon, чтобы узнать расписание биатлона."
        "\nНапиши /football, чтобы узнать расписание футбола."
        "\nНапиши /billiards, чтобы узнать расписание бильярда."
    )


@router.message(Command("subscribe"))
async def add_subscriber(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    subscriber = await orm_get_user(session, user_id)
    if subscriber:
        await message.answer('Вы уже подписаны на рассылку расписания')
    else:
        await orm_add_user(session, user_id)
        await message.answer('Вы успешно подписались на рассылку расписания')


@router.message(Command("unsubscribe"))
async def delete_subscriber(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    subscriber = await orm_get_user(session, user_id)
    if subscriber:
        await orm_delete_user(session, user_id)
        await message.answer('Вы успешно отписались от рассылки расписания')
    else:
        await message.answer('Вы не подписаны или не вообще не подписывались на рассылку расписания')


@router.message(Command("biathlon"))
async def send_biathlon_schedule(message: Message):
    schedule = await get_schedule("биатлон")
    response = (
        "\n".join(schedule) if schedule
        else "На данный момент биатлон не запланирован."
    )
    await message.answer(
        response,
        parse_mode="Markdown"
    )


@router.message(Command("billiards"))
async def send_billiards_schedule(message: Message):
    schedule = await get_schedule("бильярд")
    response = (
        "\n".join(schedule) if schedule
        else "На данный момент бильярд не запланирован."
    )
    await message.answer(
        response,
        parse_mode="Markdown"
    )


@router.message(Command("football"))
async def send_football_schedule(message: Message):
    schedule = await get_schedule("футбол")
    response = (
        "\n".join(schedule) if schedule
        else "На данный момент футбол не запланирован."
    )
    await message.answer(
        response,
        parse_mode="Markdown"
    )


@router.message()
async def echo(message: Message):
    await message.answer(
        "Для получения расписания биатлона напиши /biathlon. "
        "Для получения расписания футбола напиши /football. "
        "Для получения расписания бильярда напиши /billiards"
    )
