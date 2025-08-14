import os
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
import aiohttp

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

router = Router()

@router.message(Command("start"))
async def start_cmd(msg: Message):
    await msg.answer("Foody bot. Команды: /id, /link <CODE>")

@router.message(Command("id"))
async def id_cmd(msg: Message):
    await msg.answer(f"Ваш chat_id: {msg.chat.id}")

@router.message(Command("link"))
async def link_cmd(msg: Message):
    if not BACKEND_URL:
        await msg.answer("BACKEND_URL не задан на боте.")
        return
    parts = msg.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Пришлите: /link ABC123")
        return
    code = parts[1].strip().upper()
    payload = {"code": code, "chat_id": msg.chat.id}
    url = f"{BACKEND_URL.rstrip('/')}/api/v1/telegram/link"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as r:
                if r.status == 200:
                    data = await r.json()
                    await msg.answer(f"Успех! Привязали chat_id к мерчанту {data.get('merchant_id')}")
                else:
                    try:
                        err = await r.json()
                    except Exception:
                        err = {"detail": await r.text()}
                    await msg.answer(f"Ошибка {r.status}: {err}")
    except Exception as e:
        await msg.answer(f"Ошибка запроса: {e}")

async def main():
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN не задан"); return
    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
