from re import split

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.get import get_datas, get_user, get_orderings, get_ordering, get_data, get_events
from app.database.set import set_data
from app.handlers.admin import admin_state_handler
from app.keyboards.generator import data_keyboard_markup
from app.types.type import SystemTypes, UserTypes, OrderTypes
from app.utils import get_next_order, save_content_by_filters, send_data_to_user
from app.logger.logger import Logger

logger = Logger()


async def state_replier(message: Message, state: FSMContext):
    current_state = await state.get_state()
    event_id, action_id = current_state.split(':')
    order = get_ordering(entity_id=f"{OrderTypes.data}:{action_id}").order
    keyboards = get_datas(action_id=int(action_id), active=True, system=True, type=SystemTypes.keyboard)
    keyboard = await data_keyboard_markup(data=keyboards, message=message)
    for element in order.split(':'):
        await send_data_to_user(
            message,
            get_data(id=int(element), active=True, system=True),
            keyboard
        )


async def state_handler(message: Message, state: FSMContext):
    from app.handlers.user import start
    current_state = await state.get_state()
    if not current_state:
        return await start(message, state)
    states = current_state.split(':')
    if len(states) == 2:
        event_id, action_id = states
    else:
        if states[0].lower() == 'admin':
            return await admin_state_handler(message, state)
        elif len(states) < 2:
            return await start(message, state)
    if current_state == '0:0':
        allowed_events = get_events(active=True)
        for event in allowed_events:
            if message.text == event.name:
                order = get_ordering(entity_id=f"{OrderTypes.action}:{event.id}").order
                await state.set_state(f"{event.id}:{order.split(':')[0]}")
                return await state_replier(message, state)

    datas = get_datas(action_id=int(action_id), active=True, system=True, type=SystemTypes.filter)
    filters = []
    for type in datas:
        filters.append(type.value)
        if type.value.startswith(UserTypes.text):
            filters.append(UserTypes.text)
    # filters = [split(r"\(.*\)", data.value)[0] for data in datas]
    if not filters:
        logger.warn(
            f"No filters setted to {event_id=}, {action_id=}. Allow all."
        )
        filters.append("text(.*)")
        filters.append(UserTypes.text)
        filters.append(UserTypes.animation)
        filters.append(UserTypes.audio)
        filters.append(UserTypes.document)
        filters.append(UserTypes.photo)
        filters.append(UserTypes.sticker)
        filters.append(UserTypes.video)
        filters.append(UserTypes.voice)
        filters.append(UserTypes.contact)
        filters.append(UserTypes.poll)
        filters.append(UserTypes.location)

    if message.content_type in filters:
        await save_content_by_filters(message=message, filters=filters, action_id=int(action_id))
        if next_action := await get_next_order(OrderTypes.action, int(event_id), int(action_id)):
            await state.set_state(f"{event_id}:{next_action}")
        else:
            await message.answer(
                f"Necessary action has ended. Return to the home page.\n\n"
                f"Необходимые действия закончились. Возвращаемся на домашнюю страницу."
            )
            return await start(message, state)

        return await state_replier(message, state)

    await message.reply(
        f"Error occurred.\n"
        f"Handled content type ({message.content_type}) is not match expected filters ({filters}).\n"
        f"Try again.\n\n"
        f"Произошла ошибка.\n"
        f"Полученный тип сообщения ({message.content_type}) не совпадает с ожидаемыми фильтрами ({filters}).\n"
        f"Попробуйте еще раз."
    )
