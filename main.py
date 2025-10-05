# File: main.py
"""
Oddiy Telegram bot — General English (A1-C2) baholaydi.
Foydalanish: BOT_TOKEN muhit o'zgaruvchisiga tokenni qo'ying.
Yozuvchi: Siz GitHubga joylaysiz — fayllar quyida.

Talablar: python-telegram-bot v20.x, python-dotenv (ixtiyoriy)
"""

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import os

# State identifier
Q, = range(1)

# 10 ta test savollar (oddiy misollar)
QUESTIONS = [
    {
        "q": "1) Which is the correct sentence?",
        "opts": ["I go to school yesterday.", "I went to school yesterday.", "I going to school yesterday.", "I gone to school yesterday."],
        "a": 1,
    },
    {
        "q": "2) Choose the correct past participle of 'write':",
        "opts": ["writed", "wrote", "written", "write"],
        "a": 2,
    },
    {
        "q": "3) Fill in: 'She _____ breakfast every morning.'",
        "opts": ["eat", "eats", "eating", "ate"],
        "a": 1,
    },
    {
        "q": "4) Which word is a synonym of 'big'?",
        "opts": ["small", "huge", "tiny", "narrow"],
        "a": 1,
    },
    {
        "q": "5) Choose correct preposition: 'I am interested _____ music.'",
        "opts": ["on", "in", "at", "for"],
        "a": 1,
    },
    {
        "q": "6) Which sentence is in future simple?",
        "opts": ["I will go.", "I went.", "I go.", "I am going."],
        "a": 0,
    },
    {
        "q": "7) Choose the correct comparative: 'good' -> _______",
        "opts": ["gooder", "better", "more good", "best"],
        "a": 1,
    },
    {
        "q": "8) Which is a question?",
        "opts": ["You are coming.", "Are you coming?", "You coming.", "You will coming?"],
        "a": 1,
    },
    {
        "q": "9) Choose correct article: 'I saw _____ elephant.'",
        "opts": ["a", "an", "the", "--"],
        "a": 1,
    },
    {
        "q": "10) Which sentence is grammatically correct?",
        "opts": ["He don't like tea.", "He doesn't likes tea.", "He doesn't like tea.", "He not like tea."],
        "a": 2,
    },
]

# Ball -> CEFR daraja
def score_to_level(score, total):
    if total == 0:
        return "Noma'lum"
    pct = score / total
    if pct <= 0.2:
        return "A1"
    elif pct <= 0.4:
        return "A2"
    elif pct <= 0.6:
        return "B1"
    elif pct <= 0.8:
        return "B2"
    elif pct <= 0.9:
        return "C1"
    else:
        return "C2"

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Salom! 👋\n\n"
        "Men oddiy General English (A1-C2) test botiman.\n"
        "Test 10 ta savoldan iborat. Har bir savolda to'g'ri variantni tanlang.\n\n"
        "Boshlash uchun /test buyrug'ini bering."
    )
    await update.message.reply_text(text)

# /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/test — testni boshlash\n/retry — yana bir bor\n/help — yordam")

# /test boshlash
async def test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['score'] = 0
    context.user_data['qindex'] = 0
    return await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    i = context.user_data.get('qindex', 0)
    if i >= len(QUESTIONS):
        score = context.user_data.get('score', 0)
        level = score_to_level(score, len(QUESTIONS))
        text = f"Test tugadi!\nSiz {score}/{len(QUESTIONS)} to'g'ri javob berdingiz.\nTaklif qilingan daraja: {level}"
        await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    q = QUESTIONS[i]
    keyboard = [[opt] for opt in q['opts']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(q['q'], reply_markup=reply_markup)
    return Q

# Javoblarni qabul qilish
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    i = context.user_data.get('qindex', 0)
    text = update.message.text
    q = QUESTIONS[i]
    try:
        chosen_index = q['opts'].index(text)
    except ValueError:
        await update.message.reply_text("Iltimos, variantlardan birini tanlang.")
        return Q

    if chosen_index == q['a']:
        context.user_data['score'] += 1

    context.user_data['qindex'] = i + 1
    return await send_question(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Test bekor qilindi.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def retry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text('Yangi test boshlanadi...')
    return await test_start(update, context)


def main():
    token = os.getenv('BOT_TOKEN')
    if not token:
        print("Iltimos BOT_TOKEN muhit o'zgaruvchisini o'rnating.")
        return

    app = ApplicationBuilder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler('test', test_start)],
        states={
            Q: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('retry', retry))
    app.add_handler(conv)

    print('Bot ishga tushdi...')
    app.run_polling()


if __name__ == '__main__':
    main()
