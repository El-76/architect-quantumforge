import asyncio
import logging
import os
import rag

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot name
bot_username = 'Practicum7Bot'

# Keep user state
state = {}
state_lock = asyncio.Lock()

# Enable logging to see errors in the console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Constructing a structured help menu with deep-linked commands
    help_text = (
        "<b>Бот Practicum7</b>\n\n"
        "Команды бота:\n\n"
        f"• /start - отобразить приветствие и текущие настройки\n"
        f"• /embeddings_openai - использовать OpenAI для поиска по векторной БД\n"
        f"• /embeddings_local - использовать локальную модель для поиска по векторной БД\n"
        f"• /llm_openai - использовать OpenAI для генерации ответов\n"
        f"• /llm_local - использовать локальную модель для генерации ответов\n"
    )

    await update.message.reply_html(
        text=help_text,
        disable_web_page_preview=True  # Keeps the UI clean by removing URL previews
    )

# Define the response to the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = update.effective_user.id

    async with state_lock:
        llm_model = state.get(user_id, {}).get("llm", "local")
        embeddings_model = state.get(user_id, {}).get("embeddings", "local")

    message = f"Привет, {user.mention_html()}!\n\nЯ умею отвечать на вопросы о вымышленной вселенной Части 7 Практикума!\n\n"

    if llm_model == "openai" or embeddings_model == "openai":
        message += "Я пользуюсь платным API GPT-5.6 для"

        if llm_model == "openai":
            message += " генерации ответов"

            if embeddings_model == "openai":
                message += " и поиска по векторной БД"
        elif embeddings_model == "openai":
                message += " поиска по векторной БД"

        message += ", поэтому не задавайте мне слишком много вопросов, иначе мне придётся пойти на улицу просить подаяние!\n"

    if llm_model == "local" or embeddings_model == "local":
        message += "Я использую ресурсы локальной машины для"

        if llm_model == "local":
            message += " генерации ответов"

            if embeddings_model == "local":
                message += " и поиска по векторной БД"
        elif embeddings_model == "local":
                message += " поиска по векторной БД"

        message += ", поэтому могу отвечать очень медленно - не судите меня строго!\n"

    await update.message.reply_html(
        message
    )

async def embeddings_openai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_model(update, context, True, "embeddings", "Для поиска по векторной БД будет использоваться модель ")

async def embeddings_local(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_model(update, context, False, "embeddings", "Для поиска по векторной БД будет использоваться модель ")

async def llm_openai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_model(update, context, True, "llm", "Для ответов будет использоваться LLM-модель ")

async def llm_local(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_model(update, context, False, "llm", "Для ответов будет использоваться LLM-модель ")

async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE, is_openai: bool, key: str, message: str) -> None:
    user_id = update.effective_user.id

    if is_openai:
        model = "openai"
    else:
        model = "local"

    async with state_lock:
        state.setdefault(user_id, {})[key] = model

    await update.message.reply_html(
        message + model
    )

# Define the echo handler that repeats user text
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:    
    async with state_lock:
        user_id = update.effective_user.id

        user_state = state.get(user_id, {})

        use_openai_embeddings = user_state.get("embeddings", "local") == "openai"
        use_openai_llm = user_state.get("llm", "local") == "openai"

    # Safely repeat the exact text message sent by the user
    await update.message.reply_text(
        rag.query(update.message.text, use_openai_embeddings, use_openai_llm)
    )

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # 2. Create the Application instance
    application = Application.builder().token(token).build()

    # 3. Register command and message handlers
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("llm_openai", llm_openai))
    application.add_handler(CommandHandler("llm_local", llm_local))
    application.add_handler(CommandHandler("embeddings_openai", embeddings_openai))
    application.add_handler(CommandHandler("embeddings_local", embeddings_local))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # 4. Run the bot until you press Ctrl-C
    print("Bot is polling... Press Ctrl-C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

