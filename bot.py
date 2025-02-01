import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

# Получаем переменные окружения
TOKEN = os.getenv("TOKEN")
EMPLOYER_ID = os.getenv("EMPLOYER_ID")

# Проверка наличия обязательных переменных
if TOKEN is None or EMPLOYER_ID is None:
    raise ValueError("Не заданы переменные окружения: TOKEN или EMPLOYER_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

def get_vacancies():
    """Получение списка вакансий с hh.ru по ID компании."""
    url = f"https://api.hh.ru/vacancies?employer_id={EMPLOYER_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        logging.error(f"Ошибка запроса: {response.status_code}")
    return []

@dp.message_handler()
async def find_job(message: types.Message):
    """Обработка входящих сообщений и поиск подходящих вакансий."""
    user_text = message.text.lower()
    vacancies = get_vacancies()
    suitable_jobs = []

    for job in vacancies:
        name = job["name"].lower()
        # Некоторые вакансии могут не иметь описания, поэтому используем get с дефолтом
        description = job["snippet"].get("requirement", "").lower()

        # Если хотя бы одно из ключевых слов содержится в запросе, считаем, что вакансия подходит
        if any(word in user_text for word in [name, description]):
            suitable_jobs.append(f"{job['name']} - {job['alternate_url']}")

    if suitable_jobs:
        await message.reply("\n".join(suitable_jobs))
    else:
        await message.reply("Извините, подходящих вакансий не найдено.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
