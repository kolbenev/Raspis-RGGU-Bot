# Raspis-RGGU-Bot

Этот бот создан для удобного доступа к расписанию занятий Российского Государственного Гуманитарного Университета (РГГУ).

С его помощью студенты могут быстро узнать расписание на сегодня, завтра или предстоящую неделю. 
Основой бота служит парсер RGGU-Shedule-Parser, который ежедневно обновляет данные в 00:01,
гарантируя актуальность предоставляемой информации.

---

## Технологии, используемые в боте
- Python 3.13 — основной язык разработки.
- PostgreSQL — реляционная база данных для хранения информации о расписании.
- Aiogram — асинхронная библиотека для работы с Telegram Bot API.
- SQLAlchemy — ORM для удобной работы с базой данных.
- Alembic — инструмент для управления миграциями базы данных.
- Docker — контейнеризация приложения для упрощения развертывания и обеспечения портативности.
- Grafana - мониториниг и визуализация логов.

---

## Функционал бота.

### Основные команды

- `/start` - команда для запуска бота.
- `/settime` - команда для установки напоминания о занятиях.
- `/report` - Команда для отправки сообщения администратору.
- `/info` - вывод информации о боте.

### Функционал.

#### Для пользователя

Пользователю доступны три основные кнопки для работы с расписанием:

- **📌 На сегодня** — выводит расписание на текущий день.
- **🌅 На завтра** — выводит расписание на следующий день.
- **📆 На неделю** — выводит расписание на ближайшие 7 дней.

#### Для администратора.

Администратор имеет доступ к расширенному набору функций:

- Отправка сообщений всем пользователям.
- Просмотр количества зарегистрированных пользователей.
- Просмотр количества отправленных репортов.
- Ручное обновление расписания в боте.
- Переход в режим ответов на репорты, где можно:
- - Ответить на репорт пользователя.
- - Удалить репорт.

---

## Запуск бота

### 1. Скопируйте репозиторий на свой компьютер:
```bash
git clone https://github.com/kolbenev/Raspis-RGGU-Bot.git
cd Raspis-RGGU-Bot
```
### 2. Настройте переменные окружения.
- Перейдите в директорию `database`, создайте файл `.env` и отредактируйте его:
```bash
cd database
cp env_example .env
nano .env
```
- Перейдите в директорию `bot`, создайте файл `.env` и отредактируйте его:
```bash
cd ../bot
cp env_example .env
nano .env
```
### 3. Запустите базу данных в контейнере:
```bash
docker compose up database -d
```
Укажите в этих файлах все необходимые параметры, включая токен бота и данные для подключения к базе данных.
### 4. Запуск через Docker.
- Вернитесь в корневую папку бота и соберите Docker образ.
```bash
docker compose build
```
- Запустите контейнер с базой данных.
```bash
docker compose up database -d
```
- Запустите бота, графану и необходимые для нее зависимости.
```bash
docker compose up
```
