from telegram import Update, ReplyKeyboardMarkup, Bot
from telegram.ext import ContextTypes, MessageHandler, filters
from config import ADMIN_CHAT_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Оставить заявку", "Оставить отзыв"],
        ["Связаться с администратором"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать в бот клиники Здоровая Я!\n"
        "ООО ТИМ осуществляет свою деятельность под торговым названием Центр акушерства и гинекологии Здоровая Я.\n"
        "Выберите одну из опций ниже, чтобы продолжить.",
        reply_markup=reply_markup
    )

async def handle_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application'] = {}
    await update.message.reply_text("Пожалуйста, введите ваше имя:")
    return "NAME"

async def handle_application_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['name'] = update.message.text
    await update.message.reply_text("Введите ваш номер телефона:")
    return "PHONE"

async def handle_application_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['phone'] = update.message.text
    await update.message.reply_text("Введите комментарий (опционально) или нажмите /skip:")
    return "COMMENT"

async def handle_application_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['comment'] = update.message.text
    await update.message.reply_text("Ваша заявка принята. Ожидайте звонка.")
    # Send the application data to the admin chat
    application_data = context.user_data['application']
    bot = context.bot
    message = (
        f"New Application:\n"
        f"Name: {application_data['name']}\n"
        f"Phone Number: {application_data['phone']}\n"
        f"Comment: {application_data['comment'] or 'No comment'}"
    )
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
    return "END"

async def skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['comment'] = None
    await update.message.reply_text("Ваша заявка принята. Ожидайте звонка.")
    # Here you would send the application data to the admin chat
    return "END"

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['feedback'] = {}
    await update.message.reply_text("Пожалуйста, оставьте ваш отзыв и оценку от 1 до 5:")
    return "RATING"

async def handle_feedback_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['feedback']['rating'] = update.message.text
    await update.message.reply_text("Введите текст отзыва:")
    return "COMMENT"

async def handle_feedback_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['feedback']['comment'] = update.message.text
    await update.message.reply_text("Спасибо за ваш отзыв! Мы ценим ваше мнение.")
    # Send the feedback data to the admin chat
    feedback_data = context.user_data['feedback']
    bot = context.bot
    message = (
        f"New Feedback:\n"
        f"Rating: {feedback_data['rating']}\n"
        f"Comment: {feedback_data['comment']}"
    )
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
    return "END"

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Контактные данные клиники: +1234567890")

from telegram.ext import ConversationHandler, CommandHandler

def handle_user_commands():
    return [
        ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Оставить заявку$"), handle_application)],
            states={
                "NAME": [MessageHandler(filters.TEXT, handle_application_name)],
                "PHONE": [MessageHandler(filters.TEXT, handle_application_phone)],
                "COMMENT": [MessageHandler(filters.TEXT, handle_application_comment), CommandHandler("skip", skip_comment)],
            },
            fallbacks=[CommandHandler("cancel", start)],
        ),
        ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Оставить отзыв$"), handle_feedback)],
            states={
                "RATING": [MessageHandler(filters.TEXT, handle_feedback_rating)],
                "COMMENT": [MessageHandler(filters.TEXT, handle_feedback_comment)],
            },
            fallbacks=[CommandHandler("cancel", start)],
        ),
        MessageHandler(filters.TEXT & filters.Regex("^Связаться с администратором$"), contact_admin),
    ]
