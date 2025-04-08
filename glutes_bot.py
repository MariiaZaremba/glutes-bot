from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")  # Ми отримаємо токен з середовища

challenge = [
    "День 1: 15 присідань + 10 містків",
    "День 2: 20 присідань + 15 випадів",
    "День 3: 25 мостиків + 20 махів назад",
    "День 4: Відпочинок 🧘‍♀️",
    "День 5: 20 присідань + 20 випадів вперед",
    "День 6: 30 містків + 20 стрибків",
    "День 7: 40 присідань + 10 бурпі"
]

user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_progress:
        user_progress[user_id] = 0
    keyboard = [[InlineKeyboardButton("Сьогоднішнє тренування", callback_data='today')]]
    await update.message.reply_text(
        "Привіт! Це челендж «Пружні сідниці». Натисни, щоб отримати завдання!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == 'today':
        day = user_progress.get(user_id, 0)
        if day >= len(challenge):
            await query.edit_message_text("Ти завершила челендж 🎉")
        else:
            workout = challenge[day]
            keyboard = [[InlineKeyboardButton("✅ Виконано", callback_data='done')]]
            await query.edit_message_text(f"{workout}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'done':
        user_progress[user_id] += 1
        await query.edit_message_text("Супер! Побачимось завтра 💪")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
