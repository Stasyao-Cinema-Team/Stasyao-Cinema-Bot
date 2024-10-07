from os import getenv, mkdir
from os.path import isdir
from pathlib import Path
from re import compile, fullmatch

from typing import Union, List, Tuple, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot

from app.database.get import get_user, get_event, get_action, get_datas, get_actions, get_events, get_ordering
from app.database.models import Data, Events, Actions
from app.database.set import set_user, set_data
from app.types.type import SystemTypes, UserTypes, OrderTypes


async def prepare_user(tg_user: User):
    user = get_user(tg_id=tg_user.id)
    if not user:
        set_user(tg_uname=tg_user.username, tg_id=tg_user.id)


async def get_homepage_datas(type: Optional[Union[List[str], Tuple[str]]] = None):
    event = get_event(id=0, active=True)
    action = get_action(id=0, event_id=event.id, active=True)
    datas = get_datas(action_id=action.id, type=type, system=True, active=True)

    return datas


async def get_allowed_commands():
    _commands = get_datas(system=True, active=True, type=SystemTypes.command)
    _actions = get_actions(active=True, id=[command.action_id for command in _commands])
    _events = get_events(active=True, id=[action.event_id for action in _actions])
    result = []
    if _events and _actions and _commands:
        for _action in _actions:
            if _action.event_id in [event.id for event in _events]:
                for _command in _commands:
                    if _command.action_id == _action.id:
                        result.append(_command)
    return result


def parse_command(message: Message) -> CommandObject:
    # Separate command with arguments
    # "/command@mention arg1 arg2" -> "/command@mention", ["arg1 arg2"]
    try:
        full_command, *args = message.text.split(maxsplit=1)
    except ValueError:
        raise Exception("not enough values to unpack")

    # Separate command into valuable parts
    # "/command@mention" -> "/", ("command", "@", "mention")
    prefix, (_command, _, mention) = full_command[0], full_command[1:].partition("@")
    return CommandObject(
        prefix=prefix,
        command=_command,
        mention=mention or None,
        args=args[0] if args else None,
    )


async def send_data_to_user(
        message: Message,
        data: Data,
        keyboard: Optional[ReplyKeyboardMarkup] = None
) -> None:
    if data.type == UserTypes.text:
        await message.answer(text=data.value, reply_markup=keyboard)
        # await SendMessage(bot, chat_id=message.chat.id, text=data.value)
    if data.type == UserTypes.animation:
        await message.answer_animation(animation=FSInputFile(data.value), reply_markup=keyboard)
        # await SendAnimation(bot, chat_id=message.chat.id, animation=FSInputFile(data.value))
    if data.type == UserTypes.audio:
        await message.answer_audio(audio=FSInputFile(data.value), reply_markup=keyboard)
        # await SendAudio(bot, chat_id=message.chat.id, audio=FSInputFile(data.value))
    if data.type == UserTypes.document:
        await message.answer_document(document=FSInputFile(data.value), reply_markup=keyboard)
        # await SendDocument(bot, chat_id=message.chat.id, document=FSInputFile(data.value))
    if data.type == UserTypes.photo:
        await message.answer_photo(photo=FSInputFile(data.value), reply_markup=keyboard)
        # await SendPhoto(bot, chat_id=message.chat.id, photo=FSInputFile(data.value))
    if data.type == UserTypes.sticker:
        await message.answer_sticker(sticker=FSInputFile(data.value), reply_markup=keyboard)
        # await SendSticker(bot, chat_id=message.chat.id, sticker=FSInputFile(data.value))
    if data.type == UserTypes.video:
        await message.answer_video(video=FSInputFile(data.value), reply_markup=keyboard)
        # await SendVideo(bot, chat_id=message.chat.id, video=FSInputFile(data.value))
    if data.type == UserTypes.voice:
        await message.answer_voice(voice=FSInputFile(data.value), reply_markup=keyboard)
        # await SendVoice(bot, chat_id=message.chat.id, voice=FSInputFile(data.value))
    if data.type == UserTypes.contact:
        await message.answer_contact(
            phone_number=data.value.split(':')[0],
            first_name=data.value.split(':')[1],
            last_name=data.value.split(':')[2],
            reply_markup=keyboard
        )
        # await SendContact(bot, chat_id=message.chat.id, phone_number=data.value.split(':')[0],
        #                   first_name=data.value.split(':')[1], last_name=data.value.split(':')[2])
    if data.type == UserTypes.poll:
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=int(data.value.split(':')[0]),
            message_id=int(data.value.split(':')[1]),
            reply_markup=keyboard
        )
    if data.type == UserTypes.location:
        await message.answer_location(
            latitude=float(data.value.split(':')[0]),
            longitude=float(data.value.split(':')[1]),
            reply_markup=keyboard
        )
        # await SendLocation(bot, chat_id=message.chat.id, latitude=float(data.value.split(':')[0]),
        #                    longitude=float(data.value.split(':')[1]))


async def regex_search_by_text_filters(message: Message, filters: List[str]):
    founded_filters = list(
        filter(
            compile(r"text\(.*\)").match,
            filters
        )
    )
    founded_filters = [f.replace('text(', '')[:-1] for f in founded_filters]
    for i in founded_filters:
        if data := fullmatch(i, message.text):
            return data.group()


async def download_file(message: Message, file_id: str) -> Path:
    path = Path(
        getenv("DOWNLOAD_PATH", './data/'),
        f"{message.from_user.id}"
    )
    if not isdir(path):
        mkdir(path)
    path = Path(path, f"{file_id}")
    await message.bot.download(
        file=file_id,
        destination=path
    )
    return path


async def get_next_order(
        content_type: OrderTypes,
        parent_id: Union[
            int,
            Events.id,
            Actions.id,
            Data.id
        ],
        actual_id: Union[
            int,
            Events.id,
            Actions.id,
            Data.id
        ]
) -> Optional[str]:
    order = get_ordering(entity_id=f"{content_type}:{parent_id}").order
    if order:
        get_next = False
        for item in order.split(':'):
            if get_next:
                return int(item)
            if int(item) == actual_id:
                get_next = True
        if get_next:
            return None

        pass
    return None


async def get_previous_state():
    pass


async def save_content_by_filters(
        message: Message,
        filters: List[UserTypes],
        action_id: Union[int, Actions.id]
):
    user = get_user(tg_id=message.from_user.id)
    match message.content_type:
        case UserTypes.text:
            if UserTypes.text in filters:
                data = await regex_search_by_text_filters(
                    message,
                    filters
                )
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=data
                )
        case UserTypes.poll:
            if UserTypes.poll in filters:
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{message.chat.id}:{message.message_id}"
                )
        case UserTypes.contact:
            if UserTypes.contact in filters:
                contact = message.contact
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type,
                    value=f"{contact.phone_number}:{contact.first_name}:{contact.last_name}"
                )
        case UserTypes.location:
            if UserTypes.location in filters:
                location = message.location
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type,
                    value=f"{location.latitude}:{location.longitude}"
                )
        case UserTypes.photo:
            if UserTypes.photo in filters:
                photos = [photo.file_id for photo in message.photo]
                downloads = [await download_file(message, photo) for photo in photos]
                for download in downloads:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=message.content_type, value=f"{download}"
                    )
        case UserTypes.animation:
            if UserTypes.animation in filters:
                animation = await download_file(message, message.animation.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{animation}"
                )
        case UserTypes.audio:
            if UserTypes.audio in filters:
                audio = await download_file(message, message.audio.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{audio}"
                )
        case UserTypes.document:
            if UserTypes.document in filters:
                document = await download_file(message, message.document)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{document}"
                )
        case UserTypes.sticker:
            if UserTypes.sticker in filters:
                sticker = await download_file(message, message.sticker.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{sticker}"
                )
        case UserTypes.video:
            if UserTypes.video in filters:
                video = await download_file(message, message.video.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{video}"
                )
        case UserTypes.voice:
            if UserTypes.voice in filters:
                voice = await download_file(message, message.voice.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{voice}"
                )


async def split_buttons(buttons: List[KeyboardButton], _split_by):
    result = []
    for i in range(0, len(buttons), _split_by):
        result.append(buttons[i:i + _split_by])
    return result
