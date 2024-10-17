from typing import List
from typing import Tuple
from typing import Union

from aiogram.types import KeyboardButton
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup

from app.database.get import get_ordering
from app.database.models import Data
from app.database.models import Events
from app.types.type import OrderTypes
from app.utils import check_tg_user_is_active_admin
from app.utils import split_buttons


async def event_keyboard_markup(
        events: Union[List[Events], Tuple[Events]],
        message: Message,
        _split_by: int = 2
):
    order = get_ordering(entity_id=OrderTypes.event).order
    buttons = []
    if not order:
        buttons = [
            KeyboardButton(text=event.name) for event in events
        ]
    else:
        for element in order.split(':'):
            index = [_index for _index, event in enumerate(events) if event.id == int(element)]
            if index:
                buttons.append(
                    KeyboardButton(
                        text=events.pop(index[0]).name
                    )
                )
    buttons = await split_buttons(buttons, _split_by)
    if check_tg_user_is_active_admin(tg_id=message.from_user.id):
        buttons = [buttons[0], [KeyboardButton(text='Admin')]]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )


async def data_keyboard_markup(
        data: Union[List[Data], Tuple[Data]],
        message: Message,
        _split_by: int = 2
):
    order = get_ordering(entity_id=f"{OrderTypes.data}").order
    buttons = []
    if not order:
        buttons = [
            KeyboardButton(text=_data.value) for _data in data
        ]
    else:
        for element in order.split(':'):
            index = [_data for _data in data if _data.id == int(element)]
            if index:
                buttons.append(data.pop(index[0]).name)
    buttons = await split_buttons(buttons, _split_by)
    # user = get_user(tg_id=message.from_user.id)
    # admin = get_admin(user_id=user.id)
    # if admin and admin.active:
    #     if buttons:
    #         buttons = [buttons[0], [KeyboardButton(text='Admin')]]
    #     else:
    #         buttons = [[KeyboardButton(text='Admin')]]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )


async def buttons_markup():
    pass
