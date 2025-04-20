import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# === Настройки ===
import os
TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# === Логирование ===
logging.basicConfig(level=logging.INFO)

# === Вакансии по городам ===
ALL_JOBS = {
    "Москва": {
        "16-18": [
            "👨‍💻 Работа в магазине электроники",
            "📦 Курьер в интернет-магазин",
            "🎭 Промоутер на мероприятиях",
        ],
        "18+": [
            "💼 Офис-менеджер",
            "👷 Строитель",
            "🍽 Официант в ресторане",
        ]
    },
    "Санкт-Петербург": {
        "16-18": [
            "🎨 Работа в креативном пространстве",
            "🚲 Курьер на велосипеде",
            "🛍 Продавец в сувенирном магазине",
        ],
        "18+": [
            "🖥 Оператор колл-центра",
            "🔧 Слесарь",
            "📊 Бухгалтер-ассистент",
        ]
    }
}

# === Хранилище данных пользователя ===
user_data = {}
user_jobs = {}

# === Главное меню ===
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🏙 Выбрать город", callback_data="change_city"),
        InlineKeyboardButton("📅 Выбрать возраст", callback_data="change_age"),
        InlineKeyboardButton("🔍 Найти вакансию", callback_data="search_job")
    )
    return keyboard

# === Меню выбора города ===
def city_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for city in ALL_JOBS.keys():
        keyboard.add(InlineKeyboardButton(city, callback_data=f"city_{city}"))
    return keyboard

# === Меню выбора возраста ===
def age_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("16-18", callback_data="age_16-18"),
        InlineKeyboardButton("18+", callback_data="age_18+")
    )
    return keyboard

# === Обработчики ===
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    user_jobs[user_id] = {}
    await message.answer("🔹 Главное меню:", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == "change_city")
async def select_city(callback_query: types.CallbackQuery):
    await bot.edit_message_text(
        "🏙 Выберите ваш город:",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=city_menu()
    )

@dp.callback_query_handler(lambda c: c.data.startswith("city_"))
async def get_city(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    city = callback_query.data.split("_")[1]
    user_data[user_id]["city"] = city
    await bot.edit_message_text(
        f"✅ Город выбран: {city}\nТеперь выберите ваш возраст:",
        user_id,
        callback_query.message.message_id,
        reply_markup=age_menu()
    )

@dp.callback_query_handler(lambda c: c.data == "change_age")
async def select_age(callback_query: types.CallbackQuery):
    await bot.edit_message_text(
        "📅 Выберите ваш возраст:",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=age_menu()
    )

@dp.callback_query_handler(lambda c: c.data.startswith("age_"))
async def get_age(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    age = callback_query.data.split("_")[1]
    user_data[user_id]["age"] = age

    city = user_data[user_id]["city"]
    user_jobs[user_id] = ALL_JOBS.get(city, {}).get(age, []).copy()

    await bot.edit_message_text(
        f"✅ Возраст выбран: {age}\nВы можете найти вакансию, нажав на кнопку ниже.",
        user_id,
        callback_query.message.message_id,
        reply_markup=main_menu()
    )

@dp.callback_query_handler(lambda c: c.data == "search_job")
async def search_jobs(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    city = user_data.get(user_id, {}).get("city")
    age = user_data.get(user_id, {}).get("age")

    if not city or not age:
        await bot.edit_message_text(
            "❗ Сначала выберите город и возраст.",
            user_id,
            callback_query.message.message_id,
            reply_markup=main_menu()
        )
        return

    if not user_jobs[user_id]:  # Если вакансии закончились, перезаполняем
        user_jobs[user_id] = ALL_JOBS.get(city, {}).get(age, []).copy()

    job = user_jobs[user_id].pop(random.randrange(len(user_jobs[user_id])))  # Выбираем случайную вакансию
    await bot.edit_message_text(
        f"🔹 Вакансия: {job}",
        user_id,
        callback_query.message.message_id,
        reply_markup=main_menu()
    )

# === Запуск бота ===
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
