from os import PathLike, getenv
from pathlib import Path
from re import compile, fullmatch

from typing import Union, List, Tuple, Optional

from aiogram.filters import CommandObject
from aiogram.types import User, Message, FSInputFile, ReplyKeyboardMarkup
from aiogram import Bot

from app.database.get import get_user, get_event, get_action, get_datas, get_actions, get_events
from app.database.models import Data
from app.database.set import set_user
from app.types.type import SystemTypes, UserTypes


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
        data: List[Data],
        keyboard: Optional[ReplyKeyboardMarkup] = None
) -> None:
    for _data in data:
        if _data.type == UserTypes.text:
            await message.answer(text=_data.value, reply_markup=keyboard)
            # await SendMessage(bot, chat_id=message.chat.id, text=data.value)
        if _data.type == UserTypes.animation:
            await message.answer_animation(animation=FSInputFile(_data.value), reply_markup=keyboard)
            # await SendAnimation(bot, chat_id=message.chat.id, animation=FSInputFile(data.value))
        if _data.type == UserTypes.audio:
            await message.answer_audio(audio=FSInputFile(_data.value), reply_markup=keyboard)
            # await SendAudio(bot, chat_id=message.chat.id, audio=FSInputFile(data.value))
        if _data.type == UserTypes.document:
            await message.answer_document(document=FSInputFile(_data.value), reply_markup=keyboard)
            # await SendDocument(bot, chat_id=message.chat.id, document=FSInputFile(data.value))
        if _data.type == UserTypes.photo:
            await message.answer_photo(photo=FSInputFile(_data.value), reply_markup=keyboard)
            # await SendPhoto(bot, chat_id=message.chat.id, photo=FSInputFile(data.value))
        if _data.type == UserTypes.sticker:
            await message.answer_sticker(sticker=FSInputFile(_data.value), reply_markup=keyboard)
            # await SendSticker(bot, chat_id=message.chat.id, sticker=FSInputFile(data.value))
        if _data.type == UserTypes.video:
            await message.answer_video(video=FSInputFile(_data.value), reply_markup=keyboard)
            # await SendVideo(bot, chat_id=message.chat.id, video=FSInputFile(data.value))
        if _data.type == UserTypes.voice:
            await message.answer_voice(voice=FSInputFile(_data.value), reply_markup=keyboard)
            # await SendVoice(bot, chat_id=message.chat.id, voice=FSInputFile(data.value))
        if _data.type == UserTypes.contact:
            await message.answer_contact(
                phone_number=_data.value.split(':')[0],
                first_name=_data.value.split(':')[1],
                last_name=_data.value.split(':')[2],
                reply_markup=keyboard
            )
            # await SendContact(bot, chat_id=message.chat.id, phone_number=data.value.split(':')[0],
            #                   first_name=data.value.split(':')[1], last_name=data.value.split(':')[2])
        if _data.type == UserTypes.poll:
            await message.bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=int(_data.value.split(':')[0]),
                message_id=int(_data.value.split(':')[1]),
                reply_markup=keyboard
            )
        if _data.type == UserTypes.location:
            await message.answer_location(
                latitude=float(_data.value.split(':')[0]),
                longitude=float(_data.value.split(':')[1]),
                reply_markup=keyboard
            )
            # await SendLocation(bot, chat_id=message.chat.id, latitude=float(data.value.split(':')[0]),
            #                    longitude=float(data.value.split(':')[1]))


async def regex_search_by_text_filters(message: Message, filters: List[Data]):
    founded_filters = list(
        filter(
            compile(r"text\(.*\)").match,
            [_filter.value for _filter in filters]
        )
    )
    founded_filters = [f.replace('text(', '')[:-1] for f in founded_filters]
    for i in founded_filters:
        if data := fullmatch(i, message.text):
            return data


async def download_file(message: Message, file_id: str) -> Path:
    path = Path(
        getenv("DOWNLOAD_PATH", './data/'),
        message.from_user.id,
        file_id
    )
    await message.bot.download_file(
        file_path=file_id,
        destination=path
    )
    return path
