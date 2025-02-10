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
]

owner_commands = private + [
    BotCommand(
        command="update",
        description="обновить расписание"
    ),
]
