from typing import Union

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from app.database.get import get_user, get_admin
from app.database.models import Users
from app.states.admin import Admin

router: Router = Router(name=__name__)


async def check_tg_user_id_admin(tg_id: Union[Users.tg_id, int]):
    _user = get_user(tg_id=tg_id)
    _admin = get_admin(user_id=_user.id, active=True)
    if _user and _admin:
        return True
    return False


async def check_system_user_id_admin(user_id: Union[Users.id, int]):
    _admin = get_admin(user_id=user_id, active=True)
    if _admin:
        return True
    return False


async def admin_state_handler(message: Message, state: FSMContext):
    return await admin(message, state)


@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    from app.handlers.user import start
    if not await check_tg_user_id_admin(message.from_user.id):
        await message.reply(
            f"Hello user, {message.from_user.first_name} {message.from_user.last_name}!\n"
            f"You have not an access to this section.\n"
            f"Yankee Go Home!!!\n\n"
            f"Приветствую пользователя, {message.from_user.first_name} {message.from_user.last_name}!\n"
            f"У тебя нет доступа в данный раздел.\n"
            f"Иди Гуляй!!!",
        )
        return await start(message, state)
    await state.set_state(Admin)
    await message.reply(
        f"Hello admin, {message.from_user.first_name} {message.from_user.last_name}!\n"
        f"Current section logic not implemented yet. Try later.\n\n"
        f"Приветствую админа, {message.from_user.first_name} {message.from_user.last_name}!\n"
        f"Функционал данного раздела еще не готов. Попобуйте позже.",
    )
    return await start(message, state)
