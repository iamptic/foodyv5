import os
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiohttp import web
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


async def _run_health_server():
    app = web.Application()
    async def health(_):
        return web.json_response({"status": "ok"})
    app.add_routes([web.get('/health', health), web.get('/ready', health)])
    port = int(os.getenv("PORT", "8080"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[bot] health server on :{port}")
    # keep alive forever
    while True:
        await asyncio.sleep(3600)

async def main():
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN не задан"); return
    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(BOT_TOKEN)
    # Ensure we use long polling: Telegram may have an old webhook set for this token
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"delete_webhook warning: {e}")
    await asyncio.gather(
        dp.start_polling(bot),
        _run_health_server(),
    )

if __name__ == "__main__":
    asyncio.run(main())
