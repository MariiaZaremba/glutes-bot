from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

reminder_users = set()
user_progress = {}

TOKEN = os.getenv("BOT_TOKEN")  # Токен з Render Environment

challenge = [
    "День 1: 15 присідань + 10 містків",
    "День 2: 20 присідань + 15 випадів",
    "День 3: 25 містків + 20 махів назад",
    "День 4: Відпочинок 🧘‍♀️",
    "День 5: 20 присідань + 20 випадів вперед",
    "День 6: 30 містків + 20 стрибків",
    "День 7: 40 присідань + 10 бурпі"
]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_progress:
        user_progress[user_id] = 0

    welcome_text = (
        "Привіт! 👋\n\n"
        "Вітаю тебе у челенджі **«Пружні сідниці»** 🍑\n"
        "Кожного дня на тебе чекатиме коротке, але ефективне тренування.\n\n"
        "📄 Деталі челенджу, відповіді на часті питання та поради:\n"
        "[Натисни сюди, щоб переглянути на Notion](https://silver-telephone-654.notion.site/1c93d72a013980129f93fedd04949345?pvs=4)\n\n"
        "Обери дію нижче:"
    )

    keyboard = [
        [InlineKeyboardButton("Сьогоднішнє тренування", callback_data='today')],
        [InlineKeyboardButton("Інструкція ще раз 📘", callback_data='info')],
        [InlineKeyboardButton("Підписатись на нагадування ⏰", callback_data='remind')]
    ]

    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


# Обробка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    chat_id = query.message.chat_id

    if query.data == 'today':
        day = user_progress.get(user_id, 0)
        if day >= len(challenge):
            await context.bot.send_message(
                chat_id=chat_id,
                text="Ти завершила челендж 🎉"
            )
        else:
            workout = challenge[day]
            keyboard = [[InlineKeyboardButton("✅ Виконано", callback_data='done')]]
            await context.bot.send_message(
                chat_id=chat_id,
                text=workout,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif query.data == 'done':
        user_progress[user_id] += 1
        await context.bot.send_message(
            chat_id=chat_id,
            text="Супер! Побачимось завтра 💪"
        )

    elif query.data == 'info':
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "📘 Ось лінк на інструкцію та всі деталі:\n"
                "[Перейти на Notion](https://silver-telephone-654.notion.site/1c93d72a013980129f93fedd04949345?pvs=4)"
            ),
            parse_mode='Markdown'
        )

    elif query.data == 'remind':
        reminder_users.add(user_id)
        keyboard = [[InlineKeyboardButton("🔕 Відписатись від нагадувань", callback_data='unremind')]]
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Ти підписалась на щоденні нагадування!\nЩоранку я буду надсилати тренування прямо сюди 💌",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'unremind':
        if user_id in reminder_users:
            reminder_users.remove(user_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text="🔕 Ти успішно відписалась від щоденних нагадувань."
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❗️Тебе не було у списку підписаних."
            )


# Надсилання ранкових повідомлень
async def send_daily_reminders():
    for user_id in reminder_users:
        day = user_progress.get(user_id, 0)
        if day >= len(challenge):
            continue

        workout = challenge[day]
        text = f"🌞 Доброго ранку!\nТвоє тренування на сьогодні:\n\n*{workout}*"

        try:
            await app.bot.send_message(
                chat_id=int(user_id),
                text=text,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Не вдалося надіслати повідомлення {user_id}: {e}")


# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

# Планувальник
scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: asyncio.run(send_daily_reminders()),
    trigger='cron',
    hour=13,  # 13:00 UTC = 8:00 ранку за CST (Chicago time)
    minute=0
)
scheduler.start()

app.run_polling()
