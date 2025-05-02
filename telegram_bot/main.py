import logging
import coloredlogs
from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, LOG_LEVEL
from config import ADMIN_CHAT_ID
from bot.handlers.admin_handlers import handle_admin_notifications
from bot.handlers.user_handlers import handle_user_commands
import uvicorn
from fastapi import FastAPI
from telegram_bot.api import all_routers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clinic_info = (
        "Добро пожаловать в бот клиники Здоровая Я!\n"
        "ООО ТИМ осуществляет свою деятельность под торговым названием Центр акушерства и гинекологии Здоровая Я.\n"
        "Выберите одну из опций ниже, чтобы продолжить."
    )
    
    keyboard = [
        ["Оставить заявку", "Оставить отзыв"],
        ["Связаться с администратором"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_photo(
        photo=open('assets/image.png', 'rb'),
        caption=clinic_info,
        reply_markup=reply_markup
    )

def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    coloredlogs.install(level=LOG_LEVEL, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    
    # Register user command handlers
    for handler in handle_user_commands():
        application.add_handler(handler)
    
    application.add_handler(CommandHandler("admin_notifications", handle_admin_notifications))

    application.run_polling()

def run_fastapi():
    app = FastAPI(title="Clinic API", description="API для заявок, отзывов и статистики")
    for router in all_routers:
        app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import sys
    if "api" in sys.argv:
        run_fastapi()
    else:
        main()
