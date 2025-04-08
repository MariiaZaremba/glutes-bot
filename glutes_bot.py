from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import os

# ==== Налаштування ====
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = "@ro_mashka86"
ADMIN_CHAT_ID = None  # Заповниться після /myid

user_progress = {}
user_states = {}  # Статуси: awaiting_video

# ==== Контент по днях ====
days = [
    {
        "title": "День 1 — Старт! \U0001F680",
        "text": (
            "Привіт! \U0001F44B Вітаю у челенджі **«Пружні сідниці»** \U0001F351\n\n"
            "\U0001F4CC  Я так рада, що ти вирішила прийняти в ньому участь! Твої сіднички того варті!\n\n"
            "Для того, щоб тренування приносили максимальну користь, тобі буде необхідно оцінити поставу через техніку виконання вправи Overhead Squat (Присідання з піднятими руками). 
            За результатами цієї оцінки, ти дізнаєшся, як коригувати своє тренування, щоб воно задовольняло саме твоїм потребам та цілям.\n\n"
            "Завтра ти отримаєш інструкції з оцінки постави.\n\n"
            "Скажи, чи готова починати?\n"
        ),
        "button_text": "✅ Готова",
        "callback": "next"
    },
    {
        "title": "День 2 — Оцінка постави \U0001F9CD‍♀️",
        "text": (
            "Сьогодні ми перевіряємо твою поставу \U0001F9D0\n\n"
            "**Що таке Overhead Squat?**\n"
            "https://youtu.be/V7fdxOlG0DA?si=nR3a2AO3im9JKChG\n"
            "https://youtu.be/dTEf6yD4Gm4?si=m_sELm9L61CGdTx3\n\n"

            "# **Інструкція з відеозапису:**\n\n"
            "1️⃣ **Встанови камеру або телефон** на рівні стегон або грудей, щоб добре було видно рухи всього тіла.\n\n"
            "2️⃣ **Запиши відео** з **трьох ракурсів**:\n\n"
            "- **Фронтальний (спереду)**\n\n"
            "- **Бічний (збоку)**\n\n"
            "3️⃣ **Зроби 5-7 повторень** у звичному для себе темпі.\n\n"
            "4️⃣ **Збережи відео**, аби порівняти після челленджа.\n\n"
            "5️⃣ **Завантаж відео, якщо хочеш мій коментар \U0001F4AC\n\n\n\n"
            "📄 Чек-лист у PDF:\n"
            "[Відкрити чек-лист](https://silver-telephone-654.notion.site/1c93d72a013980129f93fedd04949345?pvs=4)"
        ),
        "button_text": "📤 Надіслати відео на перевірку",
        "callback": "send_video"
    },
    # Дні 3–6 (залишаються як раніше, скорочено для прикладу)
    {
        "title": "День 3 — Тренування 1 \U0001F4AA",
        "text": (
            "Тренування + розтяжка + зміцнення\n..."
        ),
        "button_text": "✅ Виконано",
        "callback": "next"
    },
    {
        "title": "День 6 — Завершення \U0001F389",
        "text": "Фінальне тренування, залиш відгук!",
        "button_text": "✍️ Залишити відгук",
        "callback": "next"
    }
]

# ==== Команди ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_progress:
        user_progress[user_id] = 0
    await send_day(update.effective_chat.id, user_id, context)

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = update.effective_chat.id
    await update.message.reply_text(f"✅ Твій chat_id: {ADMIN_CHAT_ID}")

# ==== Кнопки ====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    chat_id = query.message.chat_id

    current_day = user_progress.get(user_id, 0)
    if current_day >= len(days):
        return

    action = days[current_day]['callback']

    if action == 'next':
        user_progress[user_id] += 1
        if user_progress[user_id] >= len(days):
            await context.bot.send_message(chat_id=chat_id, text="🎉 Ти пройшла всі дні челенджу! Пишаюсь тобою 💛")
            return
        await context.bot.send_message(chat_id=chat_id, text=f"🌟 Твій прогрес: День {user_progress[user_id]+1} / {len(days)}")
        await send_day(chat_id, user_id, context)

    elif action == 'send_video':
        user_states[user_id] = 'awaiting_video'
        await context.bot.send_message(chat_id=chat_id, text="📹 Надішли своє відео тут, і я його отримаю 💌")

# ==== Обробка відео ====
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_states.get(user_id) == 'awaiting_video':
        user_states[user_id] = None
        name = update.effective_user.full_name
        caption = f"📥 Відео від {name} (ID: {user_id})"

        if ADMIN_CHAT_ID:
            await context.bot.copy_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id,
                caption=caption
            )
        await update.message.reply_text("✅ Дякую! Я отримала твоє відео 💌")

# ==== Надсилання контенту ====
async def send_day(chat_id, user_id, context):
    day = user_progress[user_id]
    content = days[day]
    keyboard = [[InlineKeyboardButton(content["button_text"], callback_data='callback')]]
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"*{content['title']}*\n\n{content['text']}",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(content['button_text'], callback_data='go')]]),
        disable_web_page_preview=False
    )

# ==== Запуск ====
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("myid", myid))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
app.run_polling()
