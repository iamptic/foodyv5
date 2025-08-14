# Foody Canvas Kit (Railway-ready)

Монорепозиторий с тремя сервисами: **web** (Node proxy + статика), **backend** (FastAPI), **bot** (aiogram v3).
Цель — запушить в пустой репозиторий, создать 3 сервиса в Railway, проставить ENV и получить работающее **Canvas‑основание**:
- health‑чеки,
- стабильный `POST /api/v1/merchant/register_public` (через web‑домен, без 404/502),
- рабочая связка `/link <code>` из Telegram‑бота → бекенд (запись `telegram_chat_id`).

> Визуальную витрину/CRUD офферов/резервации добавляем в следующих патчах. Этот пак — Sprint 0/1 base.

---

## Структура
```
foody-canvas-kit/
  web/       # Node 18, CommonJS proxy: /api/v1/* → BACKEND_URL, статика из web/dist
  backend/   # FastAPI + SQLAlchemy (create_all), health, регистрация, привязка Telegram
  bot/       # aiogram v3: /start, /id, /link <code> → POST на backend
  README.md
  LICENSE
  .gitignore
```

## Railway: быстрый запуск (3 сервиса)

1. Создайте новый проект в Railway.
2. **Postgres**: добавьте Managed Postgres (Service → Add → Database → Postgres).
3. Создайте **три** сервисa из этого репозитория:
   - **web** → корень `/web` (Node.js),
   - **backend** → корень `/backend` (Python),
   - **bot** → корень `/bot` (Python).

> В Railway можно создать сервис → "Deploy from GitHub" и указать **Subdirectory**.

### Build & Start команды

- **web**
  - Build: `npm ci && npm run build`
  - Start: `npm run start`
- **backend**
  - Start: `bash start.sh`
- **bot**
  - Start: `python -m bot.main`

### ENV‑матрица

- **web**
  - `BACKEND_URL` — URL backend‑сервиса Railway, напр.: `https://backend-xxxx.up.railway.app`
- **backend**
  - `DATABASE_URL` — из Railway Postgres (кнопка "Connect" → "External connection string")
  - `CORS_ORIGINS` — список доменов web/bot через запятую, напр.: `https://web-xxxx.up.railway.app,https://bot-xxxx.up.railway.app`
  - `RUN_MIGRATIONS` — `1` (создаёт таблицы при старте)
  - (опционально) `R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`
  - (опционально) `TELEGRAM_BOT_TOKEN`, `BOT_PUSH_BASE_URL`, `JWT_SECRET`, `CSV_TZ`, `APP_BASE_URL`
- **bot**
  - `TELEGRAM_BOT_TOKEN` — токен вашего бота
  - `BACKEND_URL` — URL backend‑сервиса

### Проверка (smoke)

После деплоя:

1. **health**
   - `GET https://backend.../health` → `{"status":"ok"}`
   - `GET https://web.../health` → `{"status":"ok"}`
2. **регистрация** (через web‑домен!):
   - `POST https://web.../api/v1/merchant/register_public`
     ```json
     {"phone": "+79990000000"}
     ```
   → 201 + `{ "merchant_id": "...uuid...", "link_code": "ABCD12" }`
3. **бот**: отправьте `/link ABCD12` → в ответ ожидается успех, chat_id сохранится у мерчанта.

### Важно

- Прокси **не переписывает** пути `^/api/v1/*` — фронт и сервер согласованы по префиксу.
- Node‑сервер **CommonJS** (`server.cjs`) во избежание ESM‑конфликтов на Railway.
- Backend при `RUN_MIGRATIONS=1` выполнит `create_all()` и создаст таблицы (без Alembic, для Canvas‑этапа этого достаточно).

---

## Дальше (Sprints)

- S1: в backend добавить Offers/Reservations (таблицы/CRUD), в web — минимальную витрину и ЛК.
- S2: KPI/CSV, пуши ресторанам/покупателям.
- S3: R2‑хранилище для фото с валидациями/ретраями.

---

## Лицензия
MIT


---

## Примечания по сборке

- **Backend** использует `EmailStr` из Pydantic → необходим пакет `email-validator`. Он уже добавлен в `backend/requirements.txt`.
- **Web**: из-за кэша на Railway возможна ошибка `EBUSY` при `npm ci`. В репозитории добавлен `.npmrc`, а на сервере используйте Build: `npm i --omit=dev --no-audit --no-fund`.


### Telegram bot: webhook conflict
Если при запуске видите ошибку вида
`can't use getUpdates method while webhook is active; use deleteWebhook to delete the webhook first` —
у бота остался старый вебхук. В коде бота теперь выполняется `delete_webhook(drop_pending_updates=True)`
при старте, но при необходимости можно удалить вебхук вручную через BotFather или по запросу:
`https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook?drop_pending_updates=true`
