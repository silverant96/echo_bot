import os
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Инициализация статистики
STAT_FILE = "statistics.json"
if not os.path.exists(STAT_FILE):
    with open(STAT_FILE, "w") as f:
        json.dump({}, f)


# Функция для чтения статистики
def read_statistics():
    if os.stat(STAT_FILE).st_size == 0:  # Проверяем, пуст ли файл
        return {}
    with open(STAT_FILE, "r") as f:
        return json.load(f)


# Функция для записи статистики
def write_statistics(stats):
    with open(STAT_FILE, "w") as f:
        json.dump(stats, f, indent=4)


# Фильтр ключевых слов
KEYWORDS = {
    "привет": "Приветствую! Чем могу помочь?",
    "помощь": "Вы можете задать мне любой вопрос."
}


# Эхо-функция с фильтром
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Unknown"
    message = update.message.text

    # Обновляем статистику
    stats = read_statistics()
    if user_id not in stats:
        stats[user_id] = {"username": username, "messages_count": 0}
    stats[user_id]["messages_count"] += 1
    write_statistics(stats)

    # Проверяем ключевые слова
    for keyword, response in KEYWORDS.items():
        if keyword in message.lower():
            await update.message.reply_text(response)
            return

    # Неизвестный вопрос
    if message[-1] == '?':
        await update.message.reply_text("Извините, я пока не умею отвечать на такие вопросы.")
    else: # Эхо-ответ
        await update.message.reply_text(message)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать!")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Это бот написанный для выполнения тестового задания на вакансию https://hh.ru/vacancy/116069223")


# Команда /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    stats = read_statistics()
    if user_id in stats:
        count = stats[user_id]["messages_count"]
        await update.message.reply_text(f"Вы отправили {count} сообщений.")
    else:
        await update.message.reply_text("Вы ещё не отправляли сообщений.")


# Основная функция
def main() -> None:
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()
