# AdBoard FastAPI

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.124-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)

> Платформа объявлений с чатами, рейтингом пользователей и email-уведомлениями.  
> REST API на FastAPI + WebSocket-чаты (Redis Pub/Sub) + фоновые задачи (RabbitMQ) + JWT-аутентификация + готовый Docker-деплой.

---

## 📋 Содержание

- [О проекте](#-о-проекте)
- [Возможности](#-возможности)
- [Технологии](#-технологии)
- [Быстрый старт](#-быстрый-старт)
- [Переменные окружения](#-переменные-окружения)
- [Структура проекта](#-структура-проекта)
- [API](#-api)
- [WebSocket (чаты)](#-websocket-чаты)
- [Тестирование](#-тестирование)

---

## 🗂 О проекте

**AdBoard** — API-first платформа объявлений с реалтайм-коммуникацией, системой доверия и готовым деплоем. Бэкенд, к которому можно подключить любой фронтенд или мобильное приложение.

### 💡 Проблема

Существующие платформы объявлений (Авито, OLX и аналоги) — это закрытые экосистемы: бизнес не владеет данными своих пользователей, платит комиссию с каждой сделки и не может менять правила модерации под свои нужды. Разработка собственного решения с нуля — дорого и долго.

### ✅ Решение

AdBoard — это **готовый бэкенд** для запуска собственной платформы объявлений. REST API + WebSocket позволяют подключить любой клиент: веб-сайт, мобильное приложение, Telegram-бот. Платформа разворачивается одной командой через Docker и полностью контролируется владельцем.

**Ключевые отличия от «просто CRUD-доски»:**
- 💬 **Встроенные чаты** — покупатель и продавец общаются прямо на платформе, не уходя в сторонние мессенджеры
- 🏆 **Рейтинг продавцов** — система отзывов формирует доверие между незнакомыми людьми, как на маркетплейсах
- 🛡 **Модерация** — инструменты для контроля качества объявлений без ручной проверки каждого
- 📧 **Email-уведомления** — пользователи не теряют важные события (новое сообщение, пока пользователь офлайн; результат модерации объявления)
- 🔌 **API-first** — бэкенд не привязан к конкретному фронтенду, можно запустить на вебе и в мобилке параллельно

### 🎯 Для кого

| Сценарий | Описание |
|---|---|
| Нишевый маркетплейс | Площадка для конкретной категории товаров (техника, авто, одежда) |
| Корпоративная доска | Сотрудники компании продают вещи друг другу |
| Локальное сообщество | Барахолка района, города, жилого комплекса |
| MVP стартапа | Быстрый запуск идеи без разработки с нуля |

---

## ✨ Возможности

| Функция | Описание |
|---|---|
| 🔐 Аутентификация | Регистрация, вход, JWT access/refresh токены |
| 📢 Объявления | Создание, редактирование, удаление, загрузка фото, категории |
| 💬 Чаты | Реалтайм-общение через WebSocket: сообщения, «печатает…», счётчик непрочитанных |
| ⭐ Избранное | Добавление объявлений в список избранного |
| 🏆 Рейтинг | Оценки и отзывы о пользователях |
| 📧 Email | Уведомления о новых сообщениях (офлайн-пользователям) и модерации — через очередь задач |
| 🛡 Модерация | Контроль качества объявлений |
| 📖 Документация | Автоматическая Swagger / Redoc |

---

## 🛠 Технологии

| Слой | Стек |
|---|---|
| Backend | Python 3.12, FastAPI |
| База данных | PostgreSQL 15, SQLAlchemy (async) |
| Реалтайм | WebSocket + Redis Pub/Sub |
| Фоновые задачи | taskiq + RabbitMQ (отправка email) |
| Миграции | Alembic |
| Аутентификация | JWT (access + refresh) |
| Тестирование | Pytest, pytest-asyncio, fakeredis, httpx-ws |
| Инфраструктура | Docker, docker-compose |

---

## 🚀 Быстрый старт

> **Требования:** Docker и docker-compose

```bash
# 1. Клонировать репозиторий
git clone <URL_репозитория>
cd AdBoard-FastAPI

# 2. Создать файл с переменными окружения
cp .env.example .env
# Отредактируйте .env под свои настройки

# 3. Запустить
docker compose up -d --build
```

После запуска:

| Сервис | Адрес |
|---|---|
| REST API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Redoc | http://localhost:8000/redoc |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| RabbitMQ (веб-интерфейс) | http://localhost:15672 (guest / guest) |

Письма отправляет отдельный контейнер `worker` (taskiq): приложение только ставит задачу
в RabbitMQ, поэтому запрос не ждёт SMTP, а при ошибке отправка повторяется с нарастающей задержкой.

---

## ⚙️ Переменные окружения

Скопируйте `.env.example` → `.env` и заполните:

| Переменная | Пример | Описание |
|---|---|---|
| `DB_HOST` / `DB_PORT` | `adboard-postgres` / `5432` | Хост и порт PostgreSQL |
| `DB_USER` / `DB_PASSWORD` | `postgres` / `postgres` | Пользователь и пароль БД |
| `DB_NAME` | `adboard-fastapi` | Имя базы данных |
| `SECRET_KEY` | `supersecretkey` | Секрет для подписи JWT |
| `ACCESS_TOKEN_EXPIRES_MINUTES` | `15` | Время жизни access-токена (мин) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Время жизни refresh-токена (дни) |
| `REDIS_URL` | `redis://adboard-redis:6379/0` | Redis: WebSocket pub/sub и онлайн-статус |
| `RABBITMQ_URL` | `amqp://guest:guest@adboard-rabbitmq:5672/` | Брокер фоновых задач |
| `TASK_MAX_RETRIES` | `5` | Сколько раз повторять упавшую задачу |
| `TASK_RETRY_DELAY` | `10` | Базовая задержка перед повтором (сек) |
| `EMAIL_SERVER` / `EMAIL_PORT` | `smtp.gmail.com` / `587` | SMTP-сервер (STARTTLS) |
| `EMAIL_USER` / `EMAIL_PASSWORD` | `you@gmail.com` / `password` | Логин и пароль SMTP |
| `EMAIL_FROM` / `EMAIL_FROM_NAME` | `you@gmail.com` / `AdBoard` | Отправитель писем |

---

## 📁 Структура проекта

```
AdBoard-FastAPI/
├── app/
│   ├── api/            # REST API эндпоинты (роутеры)
│   ├── core/           # Настройки, конфиг, подключение к БД, JWT
│   ├── models/         # SQLAlchemy модели
│   ├── repositories/   # Доступ к данным (запросы к БД)
│   ├── schemas/        # Pydantic схемы (запрос / ответ)
│   ├── services/       # Бизнес-логика (объявления, чаты, auth)
│   ├── storage/        # Работа с файлами
│   ├── tasks/          # Фоновые задачи taskiq (отправка email)
│   ├── ws/             # WebSocket: эндпоинт, Redis pub/sub, онлайн-статус
│   ├── main.py         # Точка входа FastAPI
│   └── Dockerfile
├── data/               # Загруженные пользователями файлы
├── migrations/         # Alembic-миграции
├── tests/              # Тесты
├── alembic.ini
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── .env.example
```

---

## 📡 API

### Аутентификация

Все приватные эндпоинты требуют заголовок:

```
Authorization: Bearer <access_token>
```

| Группа | Префикс | Что внутри |
|---|---|---|
| Auth | `/api/v1/auth` | `POST /register`, `POST /token`, `POST /token/refresh` |
| Объявления | `/api/v1/listing` | CRUD, фото, избранное, модерация |
| Чаты | `/api/v1/chat` | Список чатов, сообщения, непрочитанные |
| Пользователи | `/api/v1/user` | Профиль `/me`, отзывы `/{id}/comments` |

Полный список с параметрами — в Swagger: http://localhost:8000/docs

### Пример: регистрация и получение токена

```bash
curl -X POST http://localhost:8000/api/v1/auth/register   -H "Content-Type: application/json"   -d '{"username": "ivan", "password1": "secret", "password2": "secret"}'

# OAuth2 password flow — данные формой, не JSON
curl -X POST http://localhost:8000/api/v1/auth/token   -d "username=ivan&password=secret"
```

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

Обновление токенов: `POST /api/v1/auth/token/refresh` с телом `{"refresh_token": "eyJ..."}`.

### Пример: создание объявления

```bash
curl -X POST http://localhost:8000/api/v1/listing   -H "Authorization: Bearer <access_token>"   -H "Content-Type: application/json"   -d '{"title": "Продам велосипед", "description": "Б/у, хорошее состояние", "price": 5000, "condition": "used", "location": "Kazan", "category_ids": []}'
```

Новое объявление получает статус `moderation` и становится публичным после одобрения модератором.

---

## 💬 WebSocket (чаты)

Одно соединение на клиента, авторизация access-токеном в query-параметре
(невалидный токен — соединение отклоняется с кодом `1008`):

```
ws://localhost:8000/ws?token=<access_token>
```

События рассылаются через Redis Pub/Sub, поэтому работают при нескольких воркерах и инстансах.
Онлайн-статус пользователя тоже хранится в Redis: письмо о новом сообщении уходит только офлайн-пользователям.

**Клиент → сервер**

| Сообщение | Описание |
|---|---|
| `{"action": "subscribe", "chat_id": 5}` | Подписка на события чата (только для участников) |
| `{"action": "unsubscribe", "chat_id": 5}` | Отписка от чата |
| `{"action": "typing", "chat_id": 5}` | «Печатает…» (только в подписанном чате) |
| `{"action": "ping"}` | Ответ `{"type": "pong"}` |

**Сервер → клиент**

| Событие | Когда приходит |
|---|---|
| `new_message` | Новое сообщение в подписанном чате |
| `typing` | Собеседник печатает в подписанном чате |
| `chat_list_update` | Новое сообщение в любом чате пользователя (подписка автоматическая) |
| `unread_count` | Изменились непрочитанные (подписка автоматическая) |
| `subscribed` / `unsubscribed` / `error` | Ответы на действия клиента |

Подробнее — `GET /ws/docs` в Swagger.

---

## 🧪 Тестирование

Тестам нужна отдельная база `adboard_test` на том же сервере PostgreSQL.
Redis и RabbitMQ не нужны: в тестах используются fakeredis и in-memory брокер задач.

```bash
# Один раз: создать тестовую базу
docker compose exec postgres createdb -U <DB_USER> adboard_test

# Запустить все тесты внутри контейнера
docker compose exec app pytest
```
