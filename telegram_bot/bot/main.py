from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN
from bot.handlers.user_handlers import handle_user_commands
from bot.handlers.admin_handlers import handle_admin_notifications

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ваш бот для приёма заявок и отзывов.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("user_commands", handle_user_commands))
    application.add_handler(CommandHandler("admin_notifications", handle_admin_notifications))

    application.run_polling()

if __name__ == "__main__":
    main()
