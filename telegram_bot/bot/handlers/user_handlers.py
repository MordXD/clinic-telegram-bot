from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Оставить заявку", "Оставить отзыв"],
        ["Связаться с администратором"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я ваш бот для приёма заявок и отзывов.",
        reply_markup=reply_markup
    )

async def handle_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, введите ваше имя:")

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, оставьте ваш отзыв и оценку от 1 до 5:")

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Контактные данные клиники: +1234567890")

def handle_user_commands():
    return [
        MessageHandler(filters.TEXT & filters.Regex("^Оставить заявку$"), handle_application),
        MessageHandler(filters.TEXT & filters.Regex("^Оставить отзыв$"), handle_feedback),
        MessageHandler(filters.TEXT & filters.Regex("^Связаться с администратором$"), contact_admin),
    ]
