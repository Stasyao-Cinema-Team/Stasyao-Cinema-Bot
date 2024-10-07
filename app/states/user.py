from re import split

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.get import get_datas, get_user
from app.database.set import set_data
from app.types.type import SystemTypes, UserTypes
from app.utils import regex_search_by_text_filters, download_file


async def state_replier(message: Message, state: FSMContext):
    current_state = await state.get_state()


async def state_handler(message: Message, state: FSMContext):
    async def get_next_state():
        pass

    async def get_previous_state():
        pass

    current_state = await state.get_state()
    event_id, action_id = current_state.split(':')
    user = get_user(tg_id=message.from_user.id)
    # event = get_event(id=event_id)
    # action = get_action(id=action_id)
    datas = get_datas(action_id=action_id, active=True, system=True, type=SystemTypes.filter)
    filters = [split(r"\(.*\)", data.value)[0] for data in datas]
    if not filters:
        return await state_replier(message, state)

    if message.content_type in filters:
        if message.content_type == UserTypes.text:
            data = await regex_search_by_text_filters(message, datas)
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type, value=data
            )
        elif message.content_type == UserTypes.poll:
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type, value=f"{message.chat.id}:{message.message_id}"
            )
        elif message.content_type == UserTypes.contact:
            contact = message.contact
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type,
                value=f"{contact.phone_number}:{contact.first_name}:{contact.last_name}"
            )
        elif message.content_type == UserTypes.location:
            location = message.location
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type,
                value=f"{location.latitude}:{location.longitude}"
            )
        elif message.content_type == UserTypes.photo:
            photos = [photo.file_id for photo in message.photo]
            downloads = [download_file(message, photo) for photo in photos]
            for download in downloads:
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{download}"
                )
        elif message.content_type == UserTypes.animation:
            animation = download_file(message, message.animation.file_id)
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type, value=f"{animation}"
            )
        elif message.content_type == UserTypes.audio:
            audio = download_file(message, message.audio.file_id)
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type, value=f"{audio}"
            )
        elif message.content_type == UserTypes.document:
            document = download_file(message, message.document)
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type, value=f"{document}"
            )
        elif message.content_type == UserTypes.sticker:
            sticker = download_file(message, message.sticker.file_id)
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type, value=f"{sticker}"
            )
        elif message.content_type == UserTypes.video:
            video = download_file(message, message.video.file_id)
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type, value=f"{video}"
            )
        elif message.content_type == UserTypes.voice:
            voice = download_file(message, message.voice.file_id)
            set_data(
                action_id=action_id, create_uid=user.id,
                type=message.content_type, value=f"{voice}"
            )

        await state.set_state(await get_next_state())
        return state_replier(message, state)

    await message.reply(
        f"Error occurred.\n"
        f"Handled content type ({message.content_type}) is not match expected filters ({filters}).\n"
        f"Try again.\n\n"
        f"Произошла ошибка.\n"
        f"Полученный тип сообщения ({message.content_type}) не совпадает с ожидаемыми фильтрами ({filters}).\n"
        f"Попробуйте еще раз."
    )
