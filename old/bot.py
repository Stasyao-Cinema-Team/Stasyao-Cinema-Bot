import logging
import os
import re
import sqlite3
from datetime import datetime

import pytz
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import Message
from aiogram.utils import executor

# Настройки
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DATABASE_PATH = os.path.join('data', 'payments.db')

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
            screenshot_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Состояния для машины состояний
class PaymentState(StatesGroup):
    phone = State()
    tickets = State()
    photo = State()

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: Message):
    user = message.from_user
    await message.reply(
        f"Привет, {user.first_name}! Я бот для покупки билетов. "
        "Чтобы узнать стоимость билетов, отправь мне свой номер телефона."
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
            "Неверный формат номера телефона. Пожалуйста, введите номер в формате +7хххххххххх."
        )
        return

    await state.update_data(phone=phone)
    await message.reply(
        f"Спасибо, {user.first_name}! Теперь отправь мне количество билетов."
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
                "Количество билетов должно быть от 1 до 5. Пожалуйста, введите корректное количество."
            )
            return

        await state.update_data(tickets=tickets)
        await message.reply(
            "Деньги слать вот сюда-то столько то, Жду платежку"
        )
        await PaymentState.next()
    except ValueError:
        await message.reply(
            "Пожалуйста, введите количество билетов в виде числа."
        )

# Обработчик фотографий (скриншотов)
@dp.message_handler(content_types=types.ContentType.PHOTO, state=PaymentState.photo)
async def handle_photo(message: Message, state: FSMContext):
    user = message.from_user
    data = await state.get_data()
    phone = data.get('phone')
    tickets = data.get('tickets')

    if not phone or not tickets:
        await message.reply(
            "Пожалуйста, сначала отправьте номер телефона и количество билетов."
        )
        return

    # Получаем фотографию
    photo = message.photo[-1]
    photo_path = os.path.join('data', f"{user.username}_{tickets}.jpg")
    await photo.download(destination_file=photo_path)

    # Проверка формата скриншота
    if not photo_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        await message.reply(
            "Неверный формат скриншота. Пожалуйста, отправьте картинку в формате PNG, JPG или JPEG."
        )
        return

    # Форматируем таймстемп в московское время
    moscow_tz = pytz.timezone('Europe/Moscow')
    timestamp = datetime.now(moscow_tz).strftime('%d-%m-%Y-%H-%M-%S')

    # Записываем данные в базу данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (phone, username, timestamp, tickets, screenshot_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (phone, user.username, timestamp, tickets, photo_path))
    conn.commit()
    conn.close()

    await message.reply(
        "Спасибо! Ваш скриншот успешно сохранен и записан в базу данных."
    )
    await state.finish()

def main() -> None:
    init_db()
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()
