from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.states.admin import Admin
from app.utils import check_tg_user_is_active_admin

router: Router = Router(name=__name__)


async def admin_state_handler(message: Message, state: FSMContext):
    return await admin(message, state)


@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    from app.handlers.user import start
    if not await check_tg_user_is_active_admin(message.from_user.id):
        # TODO :WARN:
        #   Add Admin edit admins section message support
        await message.reply(
            f"Hello user, {message.from_user.first_name} {message.from_user.last_name}!\n"
            f"You have not an access to this section.\n"
            f"Yankee Go Home!!!\n"
            f"\n"
            f"Приветствую пользователя, {message.from_user.first_name} {message.from_user.last_name}!\n"
            f"У тебя нет доступа в данный раздел.\n"
            f"Иди Гуляй!!!",
        )
        return await start(message, state)
    await state.set_state(Admin)
    # await message.reply(
    #     f"Hello admin, {message.from_user.first_name} {message.from_user.last_name}!\n"
    #     f"Current section logic not implemented yet. Try later.\n"
    #     f"\n"
    #     f"Приветствую админа, {message.from_user.first_name} {message.from_user.last_name}!\n"
    #     f"Функционал данного раздела еще не готов. Попобуйте позже.",
    # )
    return await start(message, state)
