import logging
import coloredlogs
import structlog
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
from prometheus_client import make_asgi_app, Counter
from starlette.middleware.wsgi import WSGIMiddleware

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
    # Set up structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=logging.DEBUG)
    coloredlogs.install(level=LOG_LEVEL, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = structlog.get_logger()
    logger.info("Bot starting")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    for handler in handle_user_commands():
        application.add_handler(handler)
    application.add_handler(CommandHandler("admin_notifications", handle_admin_notifications))
    application.run_polling()

# Метрика для FastAPI
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])

def run_fastapi():
    app = FastAPI(title="Clinic API", description="API для заявок, отзывов и статистики")
    for router in all_routers:
        app.include_router(router)
    # Middleware для подсчёта запросов
    @app.middleware("http")
    async def prometheus_middleware(request, call_next):
        response = await call_next(request)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
        return response
    # Добавляем endpoint /metrics
    app.mount("/metrics", make_asgi_app())
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import sys
    if "api" in sys.argv:
        run_fastapi()
    else:
        main()
