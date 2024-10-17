from re import compile

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from app.database.connection import cast_data
from app.database.connection import Database
from app.database.get import get_action
from app.database.get import get_data
from app.database.get import get_event
from app.database.get import get_ordering
from app.database.models import Events
from app.keyboards.generator import event_keyboard_markup
from app.states.user import state_handler
from app.types.type import OrderTypes
from app.utils import check_tg_user_is_active_admin
from app.utils import get_allowed_commands
from app.utils import parse_command
from app.utils import prepare_user
from app.utils import send_data_to_user

router: Router = Router(name=__name__)
db = Database()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if await prepare_user(message=message):
        return
    with db.context_cursor() as cursor:
        events = cast_data(cursor.execute(
            select(Events).
            where(Events.active == True). # noqa E712
            where(Events.id != 0)
        ).fetchall())

    keyboard = await event_keyboard_markup(events=events, message=message)
    await state.set_state("0:0")

    order = get_ordering(entity_id=f"{OrderTypes.data}:0").order
    for element in order.split(':'):
        await send_data_to_user(
            message=message,
            state=state,
            data=get_data(id=int(element), active=True, system=True),
            keyboard=keyboard
        )


@router.message(Command(compile(r".*")))
async def commands(message: Message, state: FSMContext):
    from app.handlers.admin import admin
    if await prepare_user(message=message):
        return
    allowed_commands = await get_allowed_commands()
    command = parse_command(message=message).command
    if command == 'admin' and await check_tg_user_is_active_admin(tg_id=message.from_user.id):
        return await admin(message=message, state=state)

    if command not in [_command.value for _command in allowed_commands]:
        # TODO :WARN:
        #   Add Admin edit command not found message support
        await message.reply(
            "Command not found or you don't have access to this entrypoint. Return to Homepage.\n\n"
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
    return await state_handler(message=message, state=state)


@router.message()
async def common_message(message: Message, state: FSMContext):
    from app.handlers.admin import admin_state_handler
    if await prepare_user(message=message):
        return
    current_state = await state.get_state()
    if not current_state:
        return await start(message=message, state=state)
    states = current_state.split(':')
    if states[0].lower() == 'admin':
        return await admin_state_handler(message=message, state=state)
    if len(states) != 2:
        return await start(message, state)
    return await state_handler(message=message, state=state)
