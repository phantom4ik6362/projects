import json
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

TOKEN = "8536161968:AAF9B3mUezqa5KcCWDFAe3o6GKO-WrV1NMc"

bot = Bot(token=TOKEN)
dp = Dispatcher()


def load_data():
    with open("data.json", "r") as f:
        return json.load(f)


def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)


def check_new_day(data):
    today = str(datetime.date.today())

    if data["date"] != today:
        data["date"] = today
        data["spent"] = 0
        save_data(data)


# --- старт ---
@dp.message(Command("start"))
async def start(message: types.Message):

    text = """
💰 Бот учёта расходов

Как пользоваться:

1️⃣ Установить бюджет дня

/budget 500

2️⃣ Добавлять расходы просто сообщением

36 банан
120 кофе
50 такси

Бот автоматически считает остаток.

Команды:

/budget X — задать бюджет
/left — посмотреть остаток
/reset — сбросить расходы
/start — помощь

Каждый новый день расходы обнуляются автоматически.
"""

    await message.answer(text)


# --- бюджет ---
@dp.message(Command("budget"))
async def set_budget(message: types.Message):

    data = load_data()

    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Используй: /budget 500")
        return

    data["budget"] = int(parts[1])
    save_data(data)

    await message.answer(f"Бюджет установлен: {data['budget']} бат")


# --- сброс ---
@dp.message(Command("reset"))
async def reset_spent(message: types.Message):

    data = load_data()

    data["spent"] = 0
    save_data(data)

    await message.answer("Расходы сброшены")


# --- остаток ---
@dp.message(Command("left"))
async def show_left(message: types.Message):

    data = load_data()
    check_new_day(data)

    left = data["budget"] - data["spent"]

    await message.answer(
        f"Бюджет: {data['budget']} бат\n"
        f"Потрачено: {data['spent']} бат\n"
        f"Осталось: {left} бат"
    )


# --- обработка расходов ---
@dp.message()
async def handle_expense(message: types.Message):

    if not message.text:
        return

    data = load_data()
    check_new_day(data)

    first_word = message.text.split()[0]

    if not first_word.isdigit():
        return

    expense = int(first_word)

    data["spent"] += expense
    save_data(data)

    left = data["budget"] - data["spent"]

    await message.answer(
        f"Расход: {expense} бат\n"
        f"Осталось: {left} бат"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
