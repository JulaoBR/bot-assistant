import json
import os
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from decouple import config

# Carregar o token do .env
TOKEN_BOT = config("TELEGRAM_BOT_TOKEN")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 Olá! Eu sou seu assistente virtual.\n\n"
                                    "Use /salvar <texto> para salvar algo.\n"
                                    "Use /ver para ver suas notas.\n"
                                    "Use /arquivos para ver arquivos salvos.")

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN_BOT).build()

     # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()