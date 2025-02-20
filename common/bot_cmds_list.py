from aiogram.types import BotCommand

private = [
    BotCommand(
        command="biathlon",
        description="Показать расписание биатлона"
    ),
    BotCommand(
        command="football",
        description="Показать расписание футбола"
    ),
    BotCommand(
        command="billiards",
        description="Показать расписание бильярда"
    ),
    BotCommand(
        command='subscribe',
        description='Подписаться на рассылку'
    ),
    BotCommand(
        command='unsubscribe',
        description='Подписаться на рассылку'
    )
]

owner_commands = private + [
    BotCommand(
        command="update",
        description="обновить расписание"
    ),
]
