import os
import logging
import sqlite3
from datetime import datetime
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import re
from PIL import Image
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройки
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DATABASE_PATH = os.getenv('DATABASE_PATH')
TOTAL_TICKETS = int(os.getenv('TOTAL_TICKETS'))
TICKET_PRICE_OLD = int(os.getenv('TICKET_PRICE_OLD'))
TICKET_PRICE_NEW = int(os.getenv('TICKET_PRICE_NEW'))
EVENT_ADDRESS = os.getenv('EVENT_ADDRESS')
EVENT_START_TIME = os.getenv('EVENT_START_TIME')
POST_LINK = os.getenv('POST_LINK').replace(' ', '')  # Удаляем пробелы из ссылки

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к базе данных
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            username TEXT,
            timestamp TEXT,
            tickets INTEGER,
            was_in_cinema TEXT,
            screenshot_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Состояния для машины состояний
class PaymentState(StatesGroup):
    phone = State()
    was_in_cinema = State()
    tickets = State()
    photo = State()

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Обработчик команды /start внутри каждого состояния
@dp.message_handler(commands=['start'], state='*')
async def restart(message: Message, state: FSMContext):
    await state.finish()  # Сбрасываем текущее состояние
    await start(message)  # Вызываем обработчик команды /start

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: Message):
    user = message.from_user
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(tickets) FROM payments')
    total_tickets = cursor.fetchone()[0] or 0
    conn.close()

    remaining_tickets = TOTAL_TICKETS - total_tickets

    # Проверка наличия логина
    if not user.username:
        await message.reply(
            "У вас не установлено <b>имя пользователя в Telegram</b>. Пожалуйста, установите его и попробуйте снова."
            ""
            "Как это сделать:\n"
            "\n"
            f"<b>Android</b> - <a href='https://t.me/Asafev_fanzone_SPb/1/26969?single'>тыц</a>\n"
            f"<b>iOS</b> - <a href='https://t.me/Asafev_fanzone_SPb/1/26972?single'>тык</a>",
            parse_mode=types.ParseMode.HTML,
            disable_web_page_preview=True
        )
        return

    await message.reply(
        f"Привет, *{user.first_name}*! Во славу Стаса и продакшена, я распространяю билеты на третью часть документалки \"Империя без автомобилей\".\n"
        "\n"
        f"*Дата, место, время: 15.10.2024. ст. метро \"Горьковская\",ул. Александровский парк д.4/3 , Кинотеатр Великан*\n"
        "\n"
        f"*Время: Сбор в 19:00, начало в 19:30, кто опоздает того мать чата покусает!*"
        f"\n"
        f"Оставшееся количество билетов: *{remaining_tickets}*\n"
        f"Сообщи свой номер телефона в формате *+7ХХХХХХХХХХ*.",
        parse_mode=types.ParseMode.MARKDOWN
    )
    await PaymentState.phone.set()

# Обработчик сообщений с номером телефона
@dp.message_handler(state=PaymentState.phone)
async def handle_phone(message: Message, state: FSMContext):
    phone = message.text
    user = message.from_user

    # Проверка формата номера телефона
    if not re.match(r'^\+7\d{10}$', phone):
        await message.reply(
            "Неверный формат номера телефона. Пожалуйста, введите номер в формате *+7хххххххххх.*",
            parse_mode=types.ParseMode.MARKDOWN
        )
        return

    await state.update_data(phone=phone)

    await message.reply(
        "Круто! Ты был с нами раньше в кинотеатре? Напиши пожалуйста *Да* или *Нет*",
	parse_mode=types.ParseMode.MARKDOWN
    )
    await PaymentState.next()

# Обработчик сообщений с ответом о том, был ли пользователь в кинотеатре
@dp.message_handler(state=PaymentState.was_in_cinema)
async def handle_was_in_cinema(message: Message, state: FSMContext):
    was_in_cinema = message.text.lower()

    if was_in_cinema not in ["да", "нет"]:
        await message.reply(
            "Пожалуйста, выберите ответ, нажав на кнопку 'Да' или 'Нет'. Или напишите его сами."
        )
        return

    await state.update_data(was_in_cinema=was_in_cinema)
    await message.reply(
        "Понял! Сколько билетов ты хочешь взять? Только *не больше 5 шт*. Если надо больше, то пиши организаторам!",
        parse_mode=types.ParseMode.MARKDOWN,
        reply_markup=None  # Удаляем клавиатуру
    )
    await PaymentState.next()

# Обработчик сообщений с количеством билетов
@dp.message_handler(state=PaymentState.tickets)
async def handle_tickets(message: Message, state: FSMContext):
    try:
        tickets = int(message.text)

        # Проверка количества билетов
        if tickets < 1 or tickets > 5:
            await message.reply(
                "Количество билетов должно быть от 1 до 5. Если вам нужно больше билетов, пожалуйста, свяжитесь с организаторами."
            )
            return

        await state.update_data(tickets=tickets)
        await message.reply(
            "Ага, вижу!\n"
            "Теперь давай информацию по стоимости.\n"
            "\n"
            f"*Для тех кто был на первой/второй части билет стоит {TICKET_PRICE_OLD} рублей на человека*. (Мы учли в нее стоимость профицита с прошлой сходки.Будь котиком, мы будем перепроверять эту информацию)\n"
            "\n"
            f"*Для новоприбывших стоимость билета {TICKET_PRICE_NEW} рублей на человека*.\n"
            "Пожалуйста, посчитай сумму самостоятельно исходя из этой логики и *сделай платеж!*\n"
            "\n"
            "*Куда скинуть за билет?*\n"
            "По телефону +79627062823, *банк Тинькофф*\n"
            "Прудков В.\n"
            "\n"
            "*Важно! Не указывайте комментарий к платежу!*\n"
            "\n"
            "Как сделаешь - *пришли в этот чат скриншот или pdf файл!*",
            parse_mode=types.ParseMode.MARKDOWN
        )
        await PaymentState.next()
    except ValueError:
        await message.reply(
            "Пожалуйста, введите количество билетов в виде числа."
        )

# Обработчик фотографий (скриншотов)
@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.DOCUMENT], state=PaymentState.photo)
async def handle_photo(message: Message, state: FSMContext):
    user = message.from_user
    data = await state.get_data()
    phone = data.get('phone')
    tickets = data.get('tickets')
    was_in_cinema = data.get('was_in_cinema')

    if not phone or not tickets or not was_in_cinema:
        await message.reply(
            "Пожалуйста, сначала отправьте номер телефона, количество билетов и ответ о том, был ли пользователь с нами раньше в кинотеатре."
        )
        return

    # Определяем тип файла
    if message.photo:
        file = message.photo[-1]
        file_type = 'photo'
    elif message.document:
        file = message.document
        file_type = 'document'
    else:
        await message.reply(
            "Пожалуйста, отправьте скриншот или PDF файл."
        )
        return

    # Скачиваем файл
    file_info = await bot.get_file(file.file_id)
    file_path = file_info.file_path
    file_name = user.username or phone
    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        if file_type == 'photo':
            # Сохраняем изображение и конвертируем в JPEG
            photo_path = os.path.join('data', f"{file_name}_{tickets}.jpg")
            await bot.download_file(file_path, photo_path)
            img = Image.open(photo_path)
            img = img.convert('RGB')
            img.save(photo_path, 'JPEG')
        elif file_type == 'document' and file_extension in ['.pdf']:
            # Сохраняем PDF файл
            pdf_path = os.path.join('data', f"{file_name}_{tickets}{file_extension}")
            await bot.download_file(file_path, pdf_path)
            photo_path = pdf_path
        else:
            await message.reply(
                "Неверный формат файла. Пожалуйста, отправьте картинку в формате PNG, JPG, JPEG, BMP или PDF."
            )
            return

        # Форматируем таймстемп в московское время
        moscow_tz = pytz.timezone('Europe/Moscow')
        timestamp = datetime.now(moscow_tz).strftime('%d-%m-%Y-%H-%M-%S')

        # Записываем данные в базу данных
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (phone, username, timestamp, tickets, was_in_cinema, screenshot_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (phone, user.username, timestamp, tickets, was_in_cinema, photo_path))
        conn.commit()
        conn.close()

        await message.reply(
            "Все готово! Файл и информацию отправил организаторам на проверку.\n"
            "\n"
            "*Вскоре они внесут тебя в список*, а отслеживать это ты можешь в [\"Важняк\"](https://t.me/Asafev_fanzone_SPb/11781).\n"
            "*Сообщение будет в закрепе.*\n"
            "\n"
            "*Не забудь прочитать* [правила](https://t.me/Asafev_fanzone_SPb/11781/18880) и [крик матери чата](https://t.me/Asafev_fanzone_SPb/11781/18881)! *Это очень важно!*\n"
            f"\n"
            f"Если хочешь *дозаказать билеты* напиши боту */start*",
            parse_mode=types.ParseMode.MARKDOWN
        )
        await state.finish()
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        await message.reply(
            "Произошла ошибка при обработке файла. Пожалуйста, попробуйте снова."
        )

def main() -> None:
    init_db()
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()
