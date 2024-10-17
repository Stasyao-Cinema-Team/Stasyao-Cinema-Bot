from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.get import get_data
from app.database.get import get_datas
from app.database.get import get_events
from app.database.get import get_ordering
from app.handlers.admin import admin_state_handler
from app.keyboards.generator import data_keyboard_markup
from app.logger.logger import Logger
from app.types.type import OrderTypes
from app.types.type import SystemTypes
from app.types.type import UserTypes
from app.utils import get_next_order
from app.utils import prepare_user
from app.utils import save_content_by_filters
from app.utils import send_data_to_user

logger = Logger()


async def state_replier(message: Message, state: FSMContext):
    if await prepare_user(message):
        return
    current_state = await state.get_state()
    event_id, action_id = current_state.split(':')
    order = get_ordering(entity_id=f"{OrderTypes.data}:{action_id}").order
    keyboards = get_datas(action_id=int(action_id), active=True, system=True, type=SystemTypes.keyboard)
    keyboard = await data_keyboard_markup(data=keyboards, message=message)
    for element in order.split(':'):
        await send_data_to_user(
            message,
            state,
            get_data(id=int(element), active=True, system=True),
            keyboard
        )


async def state_handler(message: Message, state: FSMContext):
    from app.handlers.user import start
    current_state = await state.get_state()
    if not current_state:
        return await start(message, state)
    states = current_state.split(':')
    if states[0].lower() == 'admin':
        return await admin_state_handler(message, state)
    if len(states) == 2:
        event_id, action_id = states
    else:
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
    if UserTypes.any in filters:
        logger.warn(
            f"No filters setted to {event_id=}, {action_id=}. Allow all."
        )
        filters.append(r"text(.*(.*(\r\n|\r|\n)*.*)*.*)")
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

    if message.content_type in filters or filters == []:
        if await save_content_by_filters(message=message, filters=filters, action_id=int(action_id)) or filters == []:
            if next_action:=await get_next_order(OrderTypes.action, int(event_id), int(action_id)):
                await state.set_state(f"{event_id}:{next_action}")
            else:
                # TODO :WARN:
                #   Add Admin edit ended actions message support
                # await message.answer(
                #     f"Necessary action has ended. Return to the home page.\n"
                #     f"\n"
                #     f"\n"
                #     f"Необходимые действия закончились. Возвращаемся на домашнюю страницу."
                # )
                return await start(message, state)
    return await state_replier(message, state)

    # TODO :WARN:
    #   Add Admin edit unexpected input message support
    # await message.reply(
    #     f"Error occurred.\n"
    #     f"Handled content type ({message.content_type}) is not match expected filters ({filters}).\n"
    #     f"Try again.\n"
    #     f"\n"
    #     f"\n"
    #     f"Произошла ошибка.\n"
    #     f"Полученный тип сообщения ({message.content_type}) не совпадает с ожидаемыми фильтрами ({filters}).\n"
    #     f"Попробуйте еще раз."
    # )
