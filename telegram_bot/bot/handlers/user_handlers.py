import re
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from config import ADMIN_CHAT_ID

# ====================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================== #

def escape_markdown_v2(text: str) -> str:
    """
    Экранирует спецсимволы для MarkdownV2.
    """
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def get_initial_menu() -> ReplyKeyboardMarkup:
    """
    Возвращает начальное меню с кнопкой «Начать».
    """
    keyboard = [
        ["Начать"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_main_menu(context: ContextTypes.DEFAULT_TYPE) -> ReplyKeyboardMarkup:
    """
    Возвращает основное меню:
    - если пользователь НЕ отправил заявку, показываем «Оставить заявку» и «Связаться с администратором».
    - если ОТПРАВИЛ заявку, показываем ТОЛЬКО «Оставить отзыв».
    """
    application_submitted = context.user_data.get("application_submitted", False)
    
    if not application_submitted:
        # Пока нет заявки, показываем "Оставить заявку" и "Связаться с администратором"
        keyboard = [
            ["Оставить заявку", "Связаться с администратором"]
        ]
    else:
        # Пользователь уже оставил заявку — показываем ТОЛЬКО "Оставить отзыв"
        keyboard = [
            ["Оставить отзыв"]
        ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ====================== ОБРАБОТЧИКИ КОМАНД ====================== #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /start. Проверяет, первый ли это запуск пользователем.
    Если да, показывает кнопку «Начать». Если нет, показывает основное меню.
    """
    user_data = context.user_data
    if not user_data.get("has_started"):
        # Первый запуск: показываем кнопку «Начать»
        reply_markup = get_initial_menu()
        await update.message.reply_text(
            "Добро пожаловать в бот клиники Здоровая Я!\n"
            "ООО ТИМ (Центр акушерства и гинекологии Здоровая Я).\n"
            "Нажмите кнопку «Начать», чтобы продолжить:",
            reply_markup=reply_markup
        )
    else:
        # Не первый запуск: показываем основное меню
        reply_markup = get_main_menu(context)
        await update.message.reply_text(
            "Добро пожаловать обратно!\n"
            "Выберите одну из опций ниже, чтобы продолжить:",
            reply_markup=reply_markup
        )

async def start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик нажатия кнопки «Начать». Устанавливает флаг и показывает основное меню.
    """
    user_data = context.user_data
    user_data["has_started"] = True  # Устанавливаем, что пользователь начал взаимодействие

    reply_markup = get_main_menu(context)
    await update.message.reply_text(
        "Отлично! Вы готовы использовать бот.\n"
        "Выберите одну из опций ниже:",
        reply_markup=reply_markup
    )
    return ConversationHandler.END  # Завершаем текущий разговор

# ====================== ОБРАБОТЧИКИ «ЗАЯВКА» ====================== #

async def handle_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начинаем процесс оформления заявки.
    """
    context.user_data['application'] = {}
    await update.message.reply_text("Пожалуйста, введите ваше имя:")
    return "NAME"

async def handle_application_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['name'] = update.message.text
    await update.message.reply_text("Введите ваш номер телефона:")
    return "PHONE"

def is_valid_phone_number(phone_number: str) -> bool:
    """
    Проверка корректности номера телефона: 10–15 цифр без пробелов и символов.
    """
    return re.match(r'^\d{10,15}$', phone_number)

async def handle_application_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text
    if not is_valid_phone_number(phone_number):
        await update.message.reply_text("Пожалуйста, введите корректный номер телефона (10-15 цифр).")
        return "PHONE"
    
    context.user_data['application']['phone'] = phone_number
    await update.message.reply_text("Введите комментарий (опционально) или нажмите /skip:")
    return "COMMENT"

async def handle_application_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['comment'] = update.message.text
    return await finish_application(update, context)

async def skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['application']['comment'] = None
    return await finish_application(update, context)

async def finish_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Завершаем оформление заявки: сохраняем флаг, отправляем админу.
    """
    # Отмечаем, что пользователь оставил заявку
    context.user_data["application_submitted"] = True
    
    # Сообщаем пользователю
    await update.message.reply_text(
        "Ваша заявка принята! Теперь доступна кнопка «Оставить отзыв».\n"
        "Спасибо!"
    )

    # Отправляем заявку админу (меняем ID на @username)
    application_data = context.user_data['application']
    bot = context.bot

    user = update.effective_user
    username = user.username or 'нет'
    message = (
        f"📝 *Новая заявка:*\n"
        f"👤 *Имя:* {escape_markdown_v2(application_data['name'])}\n"
        f"📞 *Номер телефона:* `{escape_markdown_v2(application_data['phone'])}`\n"
        f"💬 *Комментарий:* {escape_markdown_v2(application_data['comment'] or 'Без комментариев')}\n\n"
        f"Пользователь: @{escape_markdown_v2(username)}"
    )
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=message,
        parse_mode="MarkdownV2"
    )

    return ConversationHandler.END  # Завершаем разговор

# ====================== ОБРАБОТЧИКИ «ОТЗЫВ» ====================== #

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Пользователь оставляет отзыв. Проверяем, подана ли вообще заявка.
    """
    application_submitted = context.user_data.get("application_submitted", False)
    if not application_submitted:
        await update.message.reply_text(
            "Вы ещё не оставили заявку. Пожалуйста, сначала оформите заявку."
        )
        return ConversationHandler.END

    context.user_data['feedback'] = {}
    keyboard = [[
        InlineKeyboardButton("👍", callback_data='1'),
        InlineKeyboardButton("👌", callback_data='2'),
        InlineKeyboardButton("😊", callback_data='3'),
        InlineKeyboardButton("😃", callback_data='4'),
        InlineKeyboardButton("🌟", callback_data='5')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Пожалуйста, выберите вашу оценку:", reply_markup=reply_markup)
    return "RATING"

async def handle_feedback_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    rating = int(query.data)
    context.user_data['feedback']['rating'] = rating

    if rating <= 3:
        await query.edit_message_text(
            text=f"Вы выбрали оценку {rating}. Пожалуйста, напишите, что вам не понравилось:"
        )
        return "DISLIKES"
    else:
        await query.edit_message_text("Спасибо за ваш отзыв! Мы ценим ваше мнение.")
        await send_feedback_to_admin(update, context)
        return ConversationHandler.END

async def handle_feedback_dislikes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['feedback']['dislikes'] = update.message.text
    await update.message.reply_text("Спасибо за ваш отзыв! Мы ценим ваше мнение.")
    await send_feedback_to_admin(update, context)
    return ConversationHandler.END

async def send_feedback_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback_data = context.user_data.get('feedback', {})
    user = update.effective_user
    bot = context.bot

    username = user.username or 'нет'
    message = (
        f"📝 *Новый отзыв:*\n"
        f"👤 *Пользователь:* {escape_markdown_v2(user.first_name)} "
        f"{escape_markdown_v2(user.last_name or '')} "
        f"\\(@{escape_markdown_v2(username)}\\)\n"
        f"⭐ *Оценка:* {escape_markdown_v2(str(feedback_data.get('rating', 'Нет оценки')))}\n"
        f"👎 *Что не понравилось:* {escape_markdown_v2(feedback_data.get('dislikes', 'Не указано'))}"
    )
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=message,
        parse_mode="MarkdownV2"
    )

# ====================== КОМАНДА «АДМИНИСТРАТОР» ====================== #

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Контактные данные клиники: +1234567890")

# ====================== ОБРАБОТЧИК НЕИЗВЕСТНЫХ СООБЩЕНИЙ ====================== #

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для неизвестных сообщений. Инструктирует пользователя использовать команду /start.
    """
    await update.message.reply_text(
        "Извините, я не понимаю эту команду.\nПожалуйста, используйте /start, чтобы начать взаимодействие со мной."
    )

# ====================== ФУНКЦИЯ ДЛЯ ConversationHandler ====================== #

def handle_user_commands():
    """
    Возвращаем список обработчиков для основного меню бота.
    """
    return [
        CommandHandler("start", start),
        # Обработчик кнопки «Начать»
        MessageHandler(filters.Regex("^Начать$"), start_button),
        
        ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Оставить заявку$"), handle_application)],
            states={
                "NAME": [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_application_name)],
                "PHONE": [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_application_phone)],
                "COMMENT": [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_application_comment),
                    CommandHandler("skip", skip_comment)
                ],
            },
            fallbacks=[CommandHandler("cancel", start)],
        ),
        ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Оставить отзыв$"), handle_feedback)],
            states={
                "RATING": [CallbackQueryHandler(handle_feedback_rating)],
                "DISLIKES": [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_dislikes)],
            },
            fallbacks=[CommandHandler("cancel", start)],
        ),
        MessageHandler(filters.TEXT & filters.Regex("^Связаться с администратором$"), contact_admin),
        # Fallback handler для неизвестных сообщений
        MessageHandler(filters.ALL, unknown_message),
    ]
