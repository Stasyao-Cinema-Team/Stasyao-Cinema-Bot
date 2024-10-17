from os import getenv
from os import mkdir
from os.path import isdir
from pathlib import Path
from re import compile
from re import fullmatch
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import KeyboardButton
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
from jinja2 import Template

from app.database.get import get_action
from app.database.get import get_actions
from app.database.get import get_admin
from app.database.get import get_data
from app.database.get import get_datas
from app.database.get import get_event
from app.database.get import get_events
from app.database.get import get_ordering
from app.database.get import get_orderings
from app.database.get import get_user
from app.database.models import Actions
from app.database.models import Admins
from app.database.models import Data
from app.database.models import Events
from app.database.models import Ordering
from app.database.models import Users
from app.database.set import set_data
from app.database.set import set_user
from app.database.update import update_user
from app.logger.logger import Logger
from app.types.type import OrderTypes
from app.types.type import SystemTypes
from app.types.type import UserTypes

logger = Logger()


@logger.time_it_debug(description="Prepairing user")
async def prepare_user(message: Message):
    system_user = get_user(tg_id=message.from_user.id)
    if await tg_username_check(message=message, system_user=system_user):
        return True
    if system_user and system_user.tg_uname != message.from_user.username:
        # TODO :WARN:
        #   Add Admin edit changed username message support
        await message.answer(
            f"Looks like you changed your *Telegram username*.\n"
            f"Updating your previous username (_{system_user.tg_uname}_) "
            f"to actual username (_{message.from_user.username}_).\n"
            f"\n"
            f"\n"
            f"Вы похоже изменили *имя пользователя Telegram*.\n"
            f"Обновляем ваш старое имя пользователя (_{system_user.tg_uname}_) "
            f"на актуальное имя пользователя (_{message.from_user.username}_)"
        )
        update_user(where_id=system_user.id, tg_uname=message.from_user.username)
    if not system_user:
        set_user(tg_uname=message.from_user.username, tg_id=message.from_user.id)


async def tg_username_check(message: Message, system_user: Users):
    if not message.from_user.username:
        # TODO :WARN:
        #   Add Admin edit need to set username message support
        await message.answer(
            "You haven't got *Telegram username* installed yet.\n"
            "Install it and try again.\n"
            "Installation Manual:\n"
            "*Android*: https://t.me/Asafev_fanzone_SPb/1/26969?single\n"
            "*IOS*: https://t.me/Asafev_fanzone_SPb/1/26972?single\n"
            "\n"
            "\n"
            "У вас не установлено *имя пользователя Telegram*.\n"
            "Пожалуйста, установите его и попробуйте снова.\n"
            "Инструкция по установке:\n"
            "*Android*: https://t.me/Asafev_fanzone_SPb/1/26969?single\n"
            "*IOS*: https://t.me/Asafev_fanzone_SPb/1/26972?single"
        )
        return True
    return False


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


@logger.time_it_debug(description="Sending data to user")
async def send_data_to_user(
        message: Message,
        state: FSMContext,
        data: Data,
        keyboard: Optional[ReplyKeyboardMarkup] = None
) -> None:
    if not keyboard.keyboard:
        keyboard = ReplyKeyboardRemove()
    if data.type == UserTypes.text:
        await message.answer(
            text=await text_templater(
                message,
                state,
                data
            ),
            reply_markup=keyboard
        )
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


async def regex_check_text_by_filters(message: Message, filters: List[str]):
    founded_filters = list(
        filter(
            compile(r"text\(.*\)").match,
            filters
        )
    )
    founded_filters = [f.replace('text(', '')[:-1] for f in founded_filters]
    for i in founded_filters:
        if fullmatch(i, message.text):
            return True
    return False


@logger.time_it_debug(description="Downloading file")
async def download_file(message: Message, file_id: str) -> Path:
    DOWNLOAD_PATH = getenv("DOWNLOAD_PATH")
    if not DOWNLOAD_PATH:
        logger.warn("\"DOWNLOAD_PATH\" environment variable not set. Use default value \"./data/\"")
        DOWNLOAD_PATH = './data/'
        if not isdir(DOWNLOAD_PATH):
            mkdir(DOWNLOAD_PATH)
    path = Path(
        DOWNLOAD_PATH,
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

    return None


async def get_previous_state():
    pass


@logger.time_it_debug(description="Saving content by filters")
async def save_content_by_filters(
        message: Message,
        filters: List[UserTypes],
        action_id: Union[int, Actions.id]
):
    user = get_user(tg_id=message.from_user.id)
    saved = False
    match message.content_type:
        case UserTypes.text:
            if UserTypes.text in filters and await regex_check_text_by_filters(message, filters):
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=message.md_text.replace('\r', '')
                )
                saved = True
        case UserTypes.poll:
            if UserTypes.poll in filters:
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{message.chat.id}:{message.message_id}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.contact:
            if UserTypes.contact in filters:
                contact = message.contact
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type,
                    value=f"{contact.phone_number}:{contact.first_name}:{contact.last_name}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.location:
            if UserTypes.location in filters:
                location = message.location
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type,
                    value=f"{location.latitude}:{location.longitude}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.photo:
            if UserTypes.photo in filters:
                photo = None
                for _photo in message.photo:
                    if photo is None:
                        photo = _photo
                    if photo.file_size < _photo.file_size:
                        photo = _photo
                photo = await download_file(message, photo.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{photo}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.animation:
            if UserTypes.animation in filters:
                animation = await download_file(message, message.animation.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{animation}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.audio:
            if UserTypes.audio in filters:
                audio = await download_file(message, message.audio.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{audio}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.document:
            if UserTypes.document in filters:
                document = await download_file(message, message.document)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{document}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.sticker:
            if UserTypes.sticker in filters:
                sticker = await download_file(message, message.sticker.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{sticker}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.video:
            if UserTypes.video in filters:
                video = await download_file(message, message.video.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{video}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
        case UserTypes.voice:
            if UserTypes.voice in filters:
                voice = await download_file(message, message.voice.file_id)
                set_data(
                    action_id=action_id, create_uid=user.id,
                    type=message.content_type, value=f"{voice}"
                )
                if message.md_text:
                    set_data(
                        action_id=action_id, create_uid=user.id,
                        type=UserTypes.text, value=message.md_text.replace('\r', '')
                    )
                saved = True
    return saved


async def split_buttons(buttons: List[KeyboardButton], _split_by):
    result = []
    for i in range(0, len(buttons), _split_by):
        result.append(buttons[i:i + _split_by])
    return result


async def text_templater(message: Message, state: FSMContext, data: Union[str, Data]):
    try:
        template = Template(data.value)
    except Exception as e:
        await message.answer(
            f"Runtime Junja2 module error while performing text completion.\n"
            f"\n"
            f"\n"
            f"Произошла ошибка Jinja2 во время выполнения заполнения текста.\n"
            f"\n"
            f"\n"
            f"```\n"
            f"{e.__str__()}\n"
            f"```"
        )
        return data
    allowed_functions = [
        get_event,
        get_events,
        get_action,
        get_actions,
        get_data,
        get_datas,
        get_ordering,
        get_orderings,
        len,
        sum,
        enumerate,
        range,
        min,
        max,
        isinstance,
        type,
        round,
        all,
        any,
        getattr,
        hasattr,
        str,
        int,
        list,
        dict,
    ]

    for func in allowed_functions:
        template.globals[func.__name__] = func

    return template.render(
        user=message.from_user,
        input_text=message.md_text,
        state=await state.get_state(),
        UserTypes=UserTypes,
        SystemTypes=SystemTypes,
        OrderTypes=OrderTypes,
        Users=Users,
        Admins=Admins,
        Events=Events,
        Actions=Actions,
        Data=Data,
        Ordering=Ordering,
    )


async def check_tg_user_is_active_admin(tg_id: Union[int, Users.tg_id]):
    user = get_user(tg_id=tg_id)
    admin = get_admin(user_id=user.id)
    if admin and admin.active:
        return True
    return False


async def check_systen_user_is_active_admin(user_id: Union[int, Users.id]):
    admin = get_admin(user_id=user_id)
    if admin and admin.active:
        return True
    return False
