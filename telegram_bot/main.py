import logging
import coloredlogs
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN, LOG_LEVEL
from config import ADMIN_CHAT_ID
from bot.handlers.admin_handlers import handle_admin_notifications
from bot.handlers.user_handlers import handle_user_commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clinic_info = (
        "О клинике\n"
        "ООО ТИМ осуществляет свою деятельность под торговым названием Центр акушерства и гинекологии Здоровая Я\n\n"
        "Лицензии и сертификаты\n"
        "Подарочные сертификаты\n"
        "Дисконтные карты\n"
        "Правовая информация\n"
        "Карточка предприятия\n"
        "Вакансии\n"
        "Общая информация\n"
        "Направления деятельности\n"
        "Юридический и фактический адрес: 426068, ул. Автозаводская, 50, г. Ижевск\n"
        "ИНН/КПП: 1840008864 / 184001001\n"
        "Лицензия: ЛО-18-01-002421, дата выдачи 27 февраля 2018 года\n"
        "Главный врач: Цатурян Юлия Григорьевна"
    )
    await update.message.reply_text(clinic_info)
    await update.message.reply_photo(photo=open('assets/image.jpg', 'rb'))

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

if __name__ == "__main__":
    main()
