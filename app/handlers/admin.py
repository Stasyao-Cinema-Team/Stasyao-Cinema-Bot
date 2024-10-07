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


@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await state.set_state(Admin)
    pass
