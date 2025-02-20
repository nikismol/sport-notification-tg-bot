from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


from database.models import Sport, User


"""Обноление данных в БД"""
async def orm_add_html(session: AsyncSession, data: str):
    query = select(Sport).where(Sport.id == 1)
    result = await session.execute(query)
    sport_entry = result.scalars().first()

    if sport_entry:
        query = update(Sport).where(
                Sport.html_code.isnot(None)
            ).values(
                html_code=data
            )

        await session.execute(query)
    else:
        sport_entry = Sport(html_code=data)
        session.add(sport_entry)

    await session.commit()


async def orm_get_html(session: AsyncSession):
    query = select(Sport.html_code).where(Sport.id == 1)
    result = await session.execute(query)
    return result.scalar()


"""Добавление в БД подписчиков"""
async def orm_add_user(session: AsyncSession, user_id: int):
    query = select(User).where(user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(User(user_id=user_id))
        await session.commit()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(user_id == user_id)
    result = await session.execute(query)
    return result.first()


async def orm_delete_user(session: AsyncSession, user_id: int):
    query = delete(User).where(user_id == user_id)
    await session.execute(query)
    await session.commit()
