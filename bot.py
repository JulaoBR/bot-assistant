import json
import os
import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, ConversationHandler, filters
from decouple import config

logging.basicConfig(level=logging.DEBUG)

# Carregar o token do .env
TOKEN_BOT = config("TELEGRAM_BOT_TOKEN")

# Estados da Conversação
DATA_LANCAMENTO, DESCRICAO, CATEGORIA, DATA_PAGAMENTO, VALOR_TOTAL, PARCELAS, CARTAO, OBSERVACAO, CONFIRMAR = range(9)

# Teclado com opções fixas (exemplo para categorias e cartões)
CATEGORIAS = [["Alimentação", "Transporte", "Lazer"], ["Saúde", "Educação", "Outros"]]
CARTOES = [["Visa", "Mastercard", "Elo"], ["Nubank", "Santander", "Outros"]]

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 Olá! Eu sou seu assistente virtual.\n\n"
                                    "Use /cadastro\n"
                                    "Use /listagem\n")
    
async def cadastro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Digite uma das opções abaixo:\n"
                                    "/lancar_despesa\n"
                                    "/lancar_receita \n")
    
async def iniciar_lancamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de lançamento de despesa"""
    await update.message.reply_text("📅 Informe a **Data de Lançamento** (Formato: DD/MM/AAAA):")
    return DATA_LANCAMENTO

async def receber_data_lancamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data_lancamento"] = update.message.text
    await update.message.reply_text("✍️ Informe a **Descrição** da despesa:")
    return DESCRICAO

async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["descricao"] = update.message.text
    await update.message.reply_text("📂 Escolha a **Categoria**:", reply_markup=ReplyKeyboardMarkup(CATEGORIAS, one_time_keyboard=True))
    return CATEGORIA

async def receber_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["categoria"] = update.message.text
    await update.message.reply_text("📆 Informe a **Data para Pagamento** (Formato: DD/MM/AAAA):")
    return DATA_PAGAMENTO

async def receber_data_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data_pagamento"] = update.message.text
    await update.message.reply_text("💰 Informe o **Valor Total da Despesa**:")
    return VALOR_TOTAL

async def receber_valor_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["valor_total"] = update.message.text
    await update.message.reply_text("📊 Informe o **Número de Parcelas**:")
    return PARCELAS

async def receber_parcelas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["parcelas"] = update.message.text
    await update.message.reply_text("💳 Escolha um **Cartão**:", reply_markup=ReplyKeyboardMarkup(CARTOES, one_time_keyboard=True))
    return CARTAO

async def receber_cartao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cartao"] = update.message.text
    await update.message.reply_text("📝 Informe uma **Observação** (ou envie '-' para deixar em branco):")
    return OBSERVACAO

async def receber_observacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["observacao"] = update.message.text

    resumo = f"""
            📌 **Resumo da Despesa**:
            📅 Data de Lançamento: {context.user_data["data_lancamento"]}
            ✍️ Descrição: {context.user_data["descricao"]}
            📂 Categoria: {context.user_data["categoria"]}
            📆 Data para Pagamento: {context.user_data["data_pagamento"]}
            💰 Valor Total: {context.user_data["valor_total"]}
            📊 Parcelas: {context.user_data["parcelas"]}
            💳 Cartão: {context.user_data["cartao"]}
            📝 Observação: {context.user_data["observacao"]}
            """
    await update.message.reply_text(resumo)
    await update.message.reply_text("✅ Confirmar lançamento? (Sim/Não)")
    return CONFIRMAR

async def confirmar_lancamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "sim":
        try:
            
            await update.message.reply_text("✅ Despesa lançada com sucesso!")
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao lançar despesa: {e}")
    else:
        await update.message.reply_text("🚫 Lançamento cancelado.")
    
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Lançamento cancelado.")
    return ConversationHandler.END

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN_BOT).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cadastro", cadastro))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("lancar_despesa", iniciar_lancamento)],
        states={
            DATA_LANCAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data_lancamento)],
            DESCRICAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)],
            CATEGORIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_categoria)],
            DATA_PAGAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data_pagamento)],
            VALOR_TOTAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_valor_total)],
            PARCELAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_parcelas)],
            CARTAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_cartao)],
            OBSERVACAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_observacao)],
            CONFIRMAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_lancamento)]
        },
        fallbacks=[CommandHandler("cancelar", cancelar)]
    )
    
    application.add_handler(conv_handler)
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()