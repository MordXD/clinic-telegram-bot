import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, Message, User
from telegram.ext import ContextTypes
from telegram_bot.bot.handlers.user_handlers import start

@pytest.mark.asyncio
async def test_start_command():
    # Мокаем объекты Update и Context
    user = User(id=123, first_name="Тест", is_bot=False)
    message = MagicMock(spec=Message)
    message.reply_text = AsyncMock()
    message.from_user = user
    update = MagicMock(spec=Update)
    update.message = message
    context = MagicMock()
    context.user_data = {}

    await start(update, context)

    # Проверяем, что reply_text был вызван с приветствием
    message.reply_text.assert_called()
    args, kwargs = message.reply_text.call_args
    assert "Добро пожаловать" in args[0] 