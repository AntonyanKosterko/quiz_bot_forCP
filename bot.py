import logging
import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Вопросы и ответы для квиза
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "Berlin", "Madrid", "Rome"],
        "answer": 0  # индекс правильного ответа
    },
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": 1
    },
    {
        "question": "Who wrote 'To Kill a Mockingbird'?",
        "options": ["Harper Lee", "Jane Austen", "Mark Twain", "Charles Dickens"],
        "answer": 0
    }
]

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция для записи ответа пользователя в базу данных
def log_user_answer(user_id, question, selected_option, correct):
    conn = sqlite3.connect('quiz_bot.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO user_answers (user_id, question, selected_option, correct)
    VALUES (?, ?, ?, ?)
    ''', (user_id, question, selected_option, correct))
    conn.commit()
    conn.close()


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['current_question'] = 0
    await ask_question(update, context)


# Функция для отправки вопроса
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = questions[context.user_data['current_question']]
    keyboard = [
        [InlineKeyboardButton(option, callback_data=str(i))] for i, option in enumerate(question["options"])
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(question["question"], reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(question["question"], reply_markup=reply_markup)


# Обработчик выбора варианта ответа
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    selected_option = int(query.data)
    current_question = context.user_data['current_question']
    correct_answer = questions[current_question]['answer']
    user_id = query.from_user.id
    question_text = questions[current_question]['question']
    selected_text = questions[current_question]['options'][selected_option]
    correct = int(selected_option == correct_answer)

    print(user_id, question_text, selected_text, correct)

    # Логируем ответ пользователя в базу данных
    log_user_answer(user_id, question_text, selected_text, correct)

    if correct:
        await query.edit_message_text(text="Correct!")
    else:
        await query.edit_message_text(
            text=f"Wrong! The correct answer is {questions[current_question]['options'][correct_answer]}.")

    context.user_data['current_question'] += 1

    if context.user_data['current_question'] < len(questions):
        await ask_question(update, context)
    else:
        await query.message.reply_text("Quiz finished! Thanks for playing.")


# Обработчик ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main() -> None:
    # Создание экземпляра Application с использованием токена из переменной окружения
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()
