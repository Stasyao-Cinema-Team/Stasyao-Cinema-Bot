from flask import Flask, render_template, send_from_directory, redirect, url_for, request, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
from dotenv import load_dotenv
import openpyxl
from io import BytesIO

# Загрузка переменных окружения из .env файла
load_dotenv()

app = Flask(__name__)
app.secret_key = 'testing_test'  # Замените на ваш секретный ключ
DATABASE_PATH = os.getenv('DATABASE_PATH')

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Пример пользователя
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'ebashit':  # Замените на ваши данные
            user = User(1)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments')
    payments = cursor.fetchall()
    cursor.execute('SELECT SUM(tickets) FROM payments')
    total_tickets = cursor.fetchone()[0] or 0
    conn.close()

    # Добавляем ссылки на скриншоты
    modified_payments = []
    for payment in payments:
        username = payment[2]
        tickets = payment[4]
        screenshot_path = payment[-1]
        if screenshot_path:
            link = f'<a href="{url_for("serve_static", filename=screenshot_path.split("/")[-1])}" target="_blank">{username}_{tickets}</a>'
            modified_payment = list(payment)
            modified_payment[-1] = link
            modified_payments.append(modified_payment)
        else:
            modified_payments.append(payment)

    return render_template('index.html', payments=modified_payments, total_tickets=total_tickets)

@app.route('/data/<path:filename>')
@login_required
def serve_static(filename):
    return send_from_directory('data', filename)

# Выгрузка данных в Excel файл
def export_data_to_excel():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments')
    payments = cursor.fetchall()
    conn.close()

    # Создание нового Excel файла
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Платежи"

    # Заголовки столбцов
    headers = ["ID", "Телефон", "Логин", "Время", "Билеты", "Был с нами раньше", "Скриншот"]
    ws.append(headers)

    # Заполнение данными
    for payment in payments:
        row = list(payment)
        username = payment[2]
        tickets = payment[4]
        screenshot_path = row[-1]
        if screenshot_path:
            row[-1] = f'=HYPERLINK("{url_for("serve_static", filename=screenshot_path.split("/")[-1], _external=True)}", "{username}_{tickets}")'
        ws.append(row)

    # Сохранение файла в памяти
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output

@app.route('/export_to_excel', methods=['POST'])
@login_required
def export_to_excel():
    output = export_data_to_excel()
    return send_file(output, download_name='payments.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
