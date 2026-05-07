import os
import time
import asyncio
import requests
import aiosqlite

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8466050585:AAFv1Ut-GsWrUStLFaaXVgfFQ1G24vbsqN0")
API_KEY = os.getenv("nxa_4cab624d390f5a6e03b1dc364fbdb68b6828b6ea")
BASE_URL = os.getenv("http://185.190.142.81")
ADMIN_ID = int(os.getenv("8502686983"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

HEADERS = {
    "X-API-Key": API_KEY
}

DB_NAME = "database.db"

# =========================
# DATABASE
# =========================

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                active_number TEXT,
                number_id TEXT,
                created_at INTEGER
            )
        ''')
        await db.commit()


async def save_session(user_id, number, number_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users
            (user_id, active_number, number_id, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, number, number_id, int(time.time())))
        await db.commit()


async def get_session(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT active_number, number_id FROM users WHERE user_id=?",
            (user_id,)
        ) as cursor:
            return await cursor.fetchone()


async def clear_session(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM users WHERE user_id=?",
            (user_id,)
        )
        await db.commit()

# =========================
# MAIN MENU
# =========================


def main_menu():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Get Number", callback_data="get_number")],
            [InlineKeyboardButton(text="📩 Check OTP", callback_data="check_otp")],
            [InlineKeyboardButton(text="💰 Balance", callback_data="balance")],
            [InlineKeyboardButton(text="❌ Cancel Session", callback_data="cancel")]
        ]
    )
    return kb

# =========================
# START
# =========================

@dp.message(Command("start"))
async def start(message: types.Message):
    text = (
        "🔥 OTP Bot Ready\n\n"
        "Choose an option below"
    )

    await message.answer(text, reply_markup=main_menu())

# =========================
# GET NUMBER
# =========================

@dp.callback_query(lambda c: c.data == "get_number")
async def get_number(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    existing = await get_session(user_id)

    if existing:
        await callback.message.answer(
            "⚠️ You already have an active number."
        )
        return

    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/numbers/get",
            json={
                "range": "99298XXX",
                "format": "national"
            },
            headers=HEADERS,
            timeout=30
        )

        data = r.json()

        if not data.get("success"):
            await callback.message.answer("❌ Failed to get number")
            return

        number = data["number"]
        number_id = data["number_id"]

        await save_session(user_id, number, number_id)

        await callback.message.answer(
            f"📱 Number: `{number}`\n\n"
            f"⏳ Waiting for OTP...",
            parse_mode="Markdown"
        )

        asyncio.create_task(poll_otp(user_id, number_id))

    except Exception as e:
        await callback.message.answer(f"Error: {e}")

# =========================
# POLL OTP
# =========================

async def poll_otp(user_id, number_id):

    for _ in range(300):

        try:
            r = requests.get(
                f"{BASE_URL}/api/v1/numbers/{number_id}/sms",
                headers=HEADERS,
                timeout=30
            )

            data = r.json()

            otp = data.get("otp")

            if otp:
                msg = data.get("message", "")
                service = data.get("service", "Unknown")

                text = (
                    f"✅ OTP Received\n\n"
                    f"🔑 OTP: `{otp}`\n"
                    f"📦 Service: {service}\n\n"
                    f"💬 Message:\n{msg}"
                )

                await bot.send_message(
                    user_id,
                    text,
                    parse_mode="Markdown"
                )

                await clear_session(user_id)
                return

        except Exception as e:
            print(e)

        await asyncio.sleep(2)

    await bot.send_message(
        user_id,
        "⌛ OTP timeout. Session expired."
    )

    await clear_session(user_id)

# =========================
# CHECK OTP
# =========================

@dp.callback_query(lambda c: c.data == "check_otp")
async def check_otp(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    session = await get_session(user_id)

    if not session:
        await callback.message.answer("❌ No active session")
        return

    number, number_id = session

    try:
        r = requests.get(
            f"{BASE_URL}/api/v1/numbers/{number_id}/sms",
            headers=HEADERS,
            timeout=30
        )

        data = r.json()

        otp = data.get("otp")

        if otp:
            await callback.message.answer(
                f"✅ OTP: `{otp}`",
                parse_mode="Markdown"
            )
        else:
            await callback.message.answer("⌛ Waiting for OTP")

    except Exception as e:
        await callback.message.answer(f"Error: {e}")

# =========================
# BALANCE
# =========================

@dp.callback_query(lambda c: c.data == "balance")
async def balance(callback: types.CallbackQuery):

    try:
        r = requests.get(
            f"{BASE_URL}/api/v1/balance",
            headers=HEADERS,
            timeout=30
        )

        data = r.json()

        bal = data.get("balance", 0)

        await callback.message.answer(
            f"💰 API Balance: {bal}"
        )

    except Exception as e:
        await callback.message.answer(f"Error: {e}")

# =========================
# CANCEL SESSION
# =========================

@dp.callback_query(lambda c: c.data == "cancel")
async def cancel(callback: types.CallbackQuery):

    user_id = callback.from_user.id

    session = await get_session(user_id)

    if not session:
        await callback.message.answer("❌ No active session")
        return

    await clear_session(user_id)

    await callback.message.answer(
        "✅ Session cancelled"
    )

# =========================
# ADMIN COMMAND
# =========================

@dp.message(Command("users"))
async def users_cmd(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            count = await cursor.fetchone()

    await message.answer(f"👥 Active Users: {count[0]}")

# =========================
# MAIN
# =========================

async def main():
    await init_db()
    print("Bot Running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
