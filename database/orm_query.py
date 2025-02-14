from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


from database.models import Sport


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
