from re import compile

from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.database.connection import Database, cast_data
from app.database.get import get_event, get_action
from app.database.models import Events
from app.keyboards.generator import event_keyboard_markup
from app.states.user import state_handler
from app.handlers.admin import check_tg_user_id_admin, admin
from app.utils import get_homepage_datas, get_allowed_commands, parse_command, send_data_to_user

router: Router = Router(name=__name__)
db = Database()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    with db.context_cursor() as cursor:
        events = cast_data(cursor.execute(
            select(Events).
            where(Events.active == True).
            where(Events.id != 0)
        ).fetchall())

    keyboard = await event_keyboard_markup(events=events, message=message)
    await state.set_state("0:0")

    datas = await get_homepage_datas()
    await send_data_to_user(message, datas, keyboard)


@router.message(Command(compile(r".*")))
async def commands(message: Message, state: FSMContext):
    allowed_commands = await get_allowed_commands()
    command = parse_command(message).command
    if await check_tg_user_id_admin(message.from_user.id) and command == 'admin':
        return await admin()

    if command not in [_command.value for _command in allowed_commands]:
        await message.reply(
            "Command not found or you don't have access to this entrypoint. Return to Homepage.\n"
            "Комманда не найдена или у вас нет к ней доступа. Возврат на Домашнюю Страницу."
        )
        return await start(message=message, state=state)

    command_action = get_action(
        id=[
            command.action_id for command in allowed_commands
            if command.value == command
        ][0],
        active=True
    )
    command_event = get_event(id=command_action.id, active=True)
    await state.set_state(f"{command_event.id}:{command_action.id}")
    await state_handler(message=message, state=state)
