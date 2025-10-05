import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Savollar va javoblar
questions = [
    ("What is the capital of England? \n(a) London \n(b) Paris \n(c) Rome", "a"),      # A1
    ("Choose the correct sentence: \n(a) He go to school. \n(b) He goes to school. \n(c) He going to school.", "b"),  # A2
    ("Complete the sentence: I have been living here ____ 2010. \n(a) since \n(b) for \n(c) at", "a"),  # B1
    ("What is the synonym of 'complicated'? \n(a) simple \n(b) complex \n(c) easy", "b"),  # B2
    ("Identify the passive voice sentence: \n(a) She writes a letter. \n(b) A letter is written by her. \n(c) She wrote a letter.", "b"),  # C1
    ("Choose the correct subjunctive mood sentence: \n(a) If I was you, I would go. \n(b) If I were you, I would go. \n(c) If I am you, I would go.", "b"),  # C2
]

level_names = ["A1", "A2", "B1", "B2", "C1", "C2"]
user_scores = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Ingliz tili darajangizni bilish uchun 6 ta savolga javob bering.\n"
        "Boshlash uchun /test buyrug‘ini yozing."
    )

# /test
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_scores[user_id] = {'score': 0, 'current': 0}
    await update.message.reply_text("Test boshlandi! Birinchi savol:")
    await ask_question(update, user_id)

# Savol berish
async def ask_question(update: Update, user_id: int):
    current = user_scores[user_id]['current']
    if current < len(questions):
        await update.message.reply_text(questions[current][0])
    else:
        score = user_scores[user_id]['score']
        if score > 0:
            level = level_names[score - 1]
        else:
            level = "No level"
        await update.message.reply_text(
            f"✅ Test tugadi!\nSizning darajangiz: {level} ({score} ta to‘g‘ri javob)"
        )
        user_scores.pop(user_id)

# Javobni qayta ishlash
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_scores:
        await update.message.reply_text("Testni boshlash uchun /test buyrug‘ini yozing.")
        return

    current = user_scores[user_id]['current']
    if current >= len(questions):
        await update.message.reply_text("Test tugadi. /test deb qayta yozing.")
        return

    user_answer = update.message.text.lower().strip()
    correct_answer = questions[current][1]

    if user_answer == correct_answer:
        user_scores[user_id]['score'] += 1
        await update.message.reply_text("✅ To‘g‘ri!")
    else:
        await update.message.reply_text(f"❌ Noto‘g‘ri! To‘g‘ri javob: {correct_answer}")

    user_scores[user_id]['current'] += 1
    await ask_question(update, user_id)

# Main
def main():
    TOKEN = "SIZNING_BOT_TOKENINGIZNI_QO‘YING"  # <-- Bu yerga tokeningizni yozing
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
