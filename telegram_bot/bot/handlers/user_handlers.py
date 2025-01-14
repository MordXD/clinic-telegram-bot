from telegram import Update, ReplyKeyboardMarkup, Bot, InlineKeyboardButton, InlineKeyboardMarkup
import re
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler
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

# Add this function to validate phone numbers
def is_valid_phone_number(phone_number):
    # Simple regex for phone number validation (e.g., 10-15 digits)
    return re.match(r'^\d{10,15}$', phone_number)

async def handle_application_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text
    if not is_valid_phone_number(phone_number):
        await update.message.reply_text("Пожалуйста, введите корректный номер телефона (10-15 цифр).")
        return "PHONE"
    
    context.user_data['application']['phone'] = phone_number
    await update.message.reply_text("Введите комментарий (опционально) или нажмите /skip:")
    return "COMMENT"  # Correct state transition

async def handle_application_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['comment'] = update.message.text
    await update.message.reply_text("Ваша заявка принята. Ожидайте звонка.")
    # Send the application data to the admin chat
    application_data = context.user_data['application']
    bot = context.bot
    message = (
         f"📝 *Новая заявка:*\n"
         f"👤 *Имя:* {application_data['name']}\n"
         f"📞 *Номер телефона:* `{application_data['phone']}`\n"
         f"💬 *Комментарий:* {application_data['comment'] or 'Без комментариев'}"
     )
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=message,
        parse_mode="MARKDOWN"
    )
    return ConversationHandler.END

async def skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['comment'] = None
    await update.message.reply_text("Ваша заявка принята. Ожидайте звонка.")
    # Here you would send the application data to the admin chat
    return ConversationHandler.END

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['feedback'] = {}
    # Create inline buttons with compact emojis for ratings
    keyboard = [
        [InlineKeyboardButton("👍", callback_data='1'),
         InlineKeyboardButton("👌", callback_data='2'),
         InlineKeyboardButton("😊", callback_data='3'),
         InlineKeyboardButton("😃", callback_data='4'),
         InlineKeyboardButton("🌟", callback_data='5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Пожалуйста, выберите вашу оценку:", reply_markup=reply_markup)
    return "RATING"

async def handle_feedback_dislikes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['feedback']['dislikes'] = update.message.text
    await update.message.reply_text("Спасибо за ваш отзыв! Мы ценим ваше мнение.")
    # Send the detailed feedback to the admin chat
    feedback_data = context.user_data.get('feedback', {})
    bot = context.bot
    message = (
        f"📝 *Новый отзыв:*\n"
        f"⭐ *Оценка:* {feedback_data.get('rating', 'Нет оценки')}\n"
        f"👎 *Что не понравилось:* {feedback_data['dislikes']}"
    )
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="MARKDOWN")
    return ConversationHandler.END
    context.user_data['feedback']['comment'] = update.message.text
    await update.message.reply_text("Спасибо за ваш отзыв! Мы ценим ваше мнение.")
    # Send the feedback data to the admin chat
    feedback_data = context.user_data.get('feedback', {})
    bot = context.bot
    message = (
        f"📝 *Новый отзыв:*\n"
        f"⭐ *Оценка:* {feedback_data['rating']}\n"
        f"👍 *Что понравилось:* {feedback_data.get('likes', 'Не указано')}\n"
        f"💬 *Комментарий:* {feedback_data['comment']}"
    )
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="MARKDOWN")
    return ConversationHandler.END

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
            fallbacks=[CommandHandler("cancel", handle_application)],
        ),
        ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Оставить отзыв$"), handle_feedback)],
            states={
                "RATING": [CallbackQueryHandler(handle_feedback_rating)],
                "DISLIKES": [MessageHandler(filters.TEXT, handle_feedback_dislikes)],
            },
            fallbacks=[CommandHandler("cancel", start)],
        ),
        MessageHandler(filters.TEXT & filters.Regex("^Связаться с администратором$"), contact_admin),
    ]
