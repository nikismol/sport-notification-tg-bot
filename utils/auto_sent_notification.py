import asyncio
import logging

from database.engine import session_maker
from database.orm_query import orm_get_all_user
from utils.get_program import get_schedule


logger = logging.getLogger(__name__)


async def check_and_send_notification(bot):
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
                async with session_maker() as db_session:
                    subscribed_users = await orm_get_all_user(db_session)

                    for user_id in subscribed_users:
                        user_id = user_id[0]
                        logger.info(f"user_is: {user_id}")
                        try:
                            await bot.send_message(user_id, message)
                        except Exception as e:
                            logger.error(
                                f"Error sending message to user {user_id}: {e}"
                            )

        except Exception as e:
            logger.error(f"Error while checking schedule: {e}")

        await asyncio.sleep(120)
