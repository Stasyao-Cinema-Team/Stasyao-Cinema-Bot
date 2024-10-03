import os
import psycopg2
import qrcode
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.types import LabeledPrice, ShippingOption, ShippingQuery, PreCheckoutQuery
from aiogram.utils.executor import start_polling
from datetime import datetime

# Замените на ваш токен
API_TOKEN = os.getenv('API_TOKEN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Цена за один билет (замените на свою)
TICKET_PRICE = 1000  # Например, 1000 рублей

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv('POSTGRES_DB', 'purchases'),
    user=os.getenv('POSTGRES_USER', 'user'),
    password=os.getenv('POSTGRES_PASSWORD', 'password'),
    host='db'
)
cursor = conn.cursor()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Сколько билетов тебе нужно?")

@dp.message_handler()
async def process_tickets_count(message: types.Message):
    try:
        tickets_count = int(message.text)
        if tickets_count <= 0:
            await message.reply("Количество билетов должно быть больше нуля.")
            return
        
        total_price = tickets_count * TICKET_PRICE
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Покупка билетов",
            description=f"Вы покупаете {tickets_count} билетов",
            provider_token=PROVIDER_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label="Билеты", amount=total_price * 100)],  # Умножаем на 100, так как сумма в копейках
            start_parameter="ticket-purchase",
            payload="custom-payload"
        )
    
    except ValueError:
        await message.reply("Пожалуйста, введите число.")

@dp.shipping_query_handler(lambda query: True)
async def process_shipping_query(shipping_query: ShippingQuery):
    await bot.answer_shipping_query(
        shipping_query.id,
        ok=True,
        shipping_options=[],
        error_message="Ошибка доставки"
    )

@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    payment_info = message.successful_payment
    tickets_count = payment_info.total_amount // (TICKET_PRICE * 100)
    
    # Сохранение информации о покупке в базу данных
    cursor.execute('''
    INSERT INTO purchases (user_id, username, tickets_count, purchase_date)
    VALUES (%s, %s, %s, %s)
    ''', (message.from_user.id, message.from_user.username, tickets_count, datetime.now()))
    conn.commit()
    
    # Генерация QR-кода (опционально)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_data = f"Username: {message.from_user.username}\n" \
              f"Tickets: {tickets_count}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    await bot.send_photo(chat_id=message.chat.id, photo=img_byte_arr, caption="Ваш QR-код:")
    
    await message.reply(f"Спасибо за покупку! Вы купили {tickets_count} билетов.")

if __name__ == '__main__':
    start_polling(dp, skip_updates=True)