# Dockerfile для бота
FROM python:3.9-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Переменные окружения
ENV API_TOKEN=${API_TOKEN}
ENV PROVIDER_TOKEN=${PROVIDER_TOKEN}

# Запуск бота
CMD ["python", "bot.py"]