from typing import Union, List, Tuple

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message

from app.database.get import get_user, get_admin
from app.database.models import Data, Events


async def data_keyboard_markup(data: Union[List[Data], Tuple[Data]]):
    return ReplyKeyboardMarkup(
        keyboard=[KeyboardButton(text=_data.value) for _data in data],
        resize_keyboard=True,
        one_time_keyboard=True
    )


async def event_keyboard_markup(
        events: Union[List[Events], Tuple[Events]],
        message: Message,
        _split_by: int = 2
):
    async def split_buttons(buttons: List[KeyboardButton]):
        result = []
        for i in range(0, len(buttons), _split_by):
            result.append(buttons[i:i + _split_by])
        return result

    buttons = [
        KeyboardButton(text=event.name) for event in events
    ]
    buttons = await split_buttons(buttons)
    user = get_user(tg_id=message.from_user.id)
    admin = get_admin(user_id=user.id)
    if admin and admin.active:
        buttons = [buttons[0], [KeyboardButton(text='Admin')]]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
