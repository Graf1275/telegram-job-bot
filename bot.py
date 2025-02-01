import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

# Получаем токены и ID компании из переменных окружения
TOKEN = os.getenv("TOKEN")
EMPLOYER_ID = os.getenv("EMPLOYER_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Логирование для отладки
logging.basicConfig(level=logging.INFO)

# Функция для получения вакансий с HH.ru
def get_vacancies():
    url = f"https://api.hh.ru/vacancies?employer_id={EMPLOYER_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("items", [])
    return []

# Функция обработки сообщений от пользователей
@dp.message_handler()
async def find_job(message: types.Message):
    user_text = message.text.lower()
    vacancies = get_vacancies()
    suitable_jobs = []

    for job in vacancies:
        name = job["name"].lower()
        description = job["snippet"].get("requirement", "").lower()

        if any(word in user_text for word in [name, description]):
            suitable_jobs.append(f"{job['name']} - {job['alternate_url']}")

    if suitable_jobs:
        await message.reply("\n".join(suitable_jobs))
    else:
        await message.reply("Извините, подходящих вакансий не найдено.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
