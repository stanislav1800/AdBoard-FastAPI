# AdBoard FastAPI

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)

> Платформа объявлений с чатами, рейтингом пользователей и email-уведомлениями.  
> REST API на FastAPI + WebSocket-чаты + JWT-аутентификация + готовый Docker-деплой.

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
- 📧 **Email-уведомления** — пользователи не теряют важные события (новое сообщение, ответ на объявление)
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
| 📢 Объявления | Создание, редактирование, удаление, поиск |
| 💬 Чаты | Реалтайм-общение между пользователями через WebSocket |
| ⭐ Избранное | Добавление объявлений в список избранного |
| 🏆 Рейтинг | Комментарии и оценки пользователей |
| 📧 Email | Уведомления о ключевых событиях |
| 🛡 Модерация | Контроль качества объявлений |
| 📖 Документация | Автоматическая Swagger / Redoc |

---

## 🛠 Технологии

| Слой | Стек |
|---|---|
| Backend | Python 3.11, FastAPI |
| База данных | PostgreSQL 15, SQLAlchemy (async) |
| Реалтайм | WebSocket |
| Миграции | Alembic |
| Аутентификация | JWT (access + refresh) |
| Тестирование | Pytest, pytest-asyncio |
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

---

## ⚙️ Переменные окружения

Скопируйте `.env.example` → `.env` и заполните:

| Переменная | Пример | Описание |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@db/adboard` | Строка подключения к БД |
| `SECRET_KEY` | `supersecretkey` | Секрет для JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Время жизни access-токена (мин) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Время жизни refresh-токена (дни) |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP-сервер для email |
| `SMTP_PORT` | `587` | SMTP-порт |
| `SMTP_USER` | `you@gmail.com` | Email отправителя |
| `SMTP_PASSWORD` | `password` | Пароль SMTP |

---

## 📁 Структура проекта

```
AdBoard-FastAPI/
├── app/
│   ├── api/            # REST API эндпоинты (роутеры)
│   ├── models/         # SQLAlchemy модели
│   ├── schemas/        # Pydantic схемы (запрос / ответ)
│   ├── services/       # Бизнес-логика (чаты, email и т.д.)
│   ├── storage/        # Работа с файлами
│   └── core/           # Настройки, конфиг, подключение к БД
├── data/               # Загруженные пользователями файлы
├── migrations/         # Alembic-миграции
├── tests/              # Тесты
├── Dockerfile
├── docker-compose.yml
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

| Эндпоинт | Метод | Описание |
|---|---|---|
| `/api/v1/auth/register` | POST | Регистрация |
| `/api/v1/auth/token` | POST | Получение токенов |
| `/api/v1/auth/refresh` | POST | Обновление access-токена |

### Пример: получение токена

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'
```

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Пример: создание объявления

```bash
curl -X POST http://localhost:8000/api/v1/ads/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Продам велосипед", "description": "Б/у, хорошее состояние", "price": 5000}'
```

---

## 💬 WebSocket (чаты)

Подключение к WebSocket требует валидный JWT-токен в query-параметре:

```
ws://localhost:8000/chat/{chat_id}/?token=<access_token>
```

| Эндпоинт | Описание |
|---|---|
| `ws://.../chat/{chat_id}/` | Подключение к чату |
| `ws://.../chat_list/` | Список чатов пользователя |
| `ws://.../unread_count/` | Количество непрочитанных сообщений |

---

## 🧪 Тестирование

```bash
# Запустить все тесты внутри контейнера
docker compose exec app pytest

# С отчётом о покрытии
docker compose exec app pytest --cov=app --cov-report=term-missing
```
