import json
import re
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8536161968:AAF9B3mUezqa5KcCWDFAe3o6GKO-WrV1NMc"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "data.json"


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def check_new_day(data):
    today = datetime.now().strftime("%Y-%m-%d")

    if data["date"] != today:
        data["date"] = today
        data["spent"] = 0
        data["records"] = []
        save_data(data)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    text = (
        "Бот учета расходов\n\n"
        "Команды:\n"
        "/budget 500 — установить бюджет\n"
        "/left — остаток бюджета\n"
        "/reset — сброс расходов\n"
        "/today — список расходов\n\n"
        "Просто пишите расходы:\n"
        "36 банан"
    )

    await message.answer(text)


@dp.message_handler(commands=["budget"])
async def set_budget(message: types.Message):

    data = load_data()
    check_new_day(data)

    parts = message.text.split()

    if len(parts) != 2:
        await message.answer("Пример: /budget 500")
        return

    try:
        amount = int(parts[1])
    except:
        await message.answer("Введите число")
        return

    data["budget"] = amount
    save_data(data)

    await message.answer(f"Бюджет установлен: {amount} бат")


@dp.message_handler(commands=["left"])
async def left(message: types.Message):

    data = load_data()
    check_new_day(data)

    left = data["budget"] - data["spent"]

    await message.answer(
        f"Бюджет: {data['budget']}\n"
        f"Потрачено: {data['spent']}\n"
        f"Остаток: {left}"
    )


@dp.message_handler(commands=["reset"])
async def reset(message: types.Message):

    data = load_data()

    data["spent"] = 0
    data["records"] = []

    save_data(data)

    await message.answer("Расходы сброшены")


@dp.message_handler(commands=["today"])
async def today(message: types.Message):

    data = load_data()
    check_new_day(data)

    if len(data["records"]) == 0:
        await message.answer("Сегодня расходов нет")
        return

    text = "За сегодня:\n"

    for r in data["records"]:
        text += r + "\n"

    await message.answer(text)


@dp.message_handler()
async def handle_expense(message: types.Message):

    text = message.text

    match = re.search(r"\d+", text)

    if not match:
        return

    amount = int(match.group())

    data = load_data()
    check_new_day(data)

    data["spent"] += amount
    data["records"].append(text)

    save_data(data)

    left = data["budget"] - data["spent"]

    response = (
        f"Добавлено: {amount}\n"
        f"Потрачено: {data['spent']}\n"
        f"Остаток: {left}"
    )

    if left < 0:
        response += f"\n⚠️ Бюджет превышен на {abs(left)}"

    await message.answer(response)


if __name__ == "__main__":
    executor.start_polling(dp)
