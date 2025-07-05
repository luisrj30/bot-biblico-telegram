import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (localmente)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("A variável de ambiente BOT_TOKEN não foi definida!")

# Configuração de log
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Base de temas bíblicos (exemplo)
BASE_TEMAS = {
    "amor": {
        "versiculo": "1 Coríntios 13:4-7",
        "texto": "O amor é paciente e bondoso. O amor não é ciumento, não se gaba, não é orgulhoso...",
        "explicacao": "Mostra como o amor verdadeiro age com bondade e paciência.",
        "aplicacao": "Aplique sendo paciente com os outros, mesmo em conflitos.",
        "materia": "https://www.jw.org/pt/biblioteca/revistas/a-despertai-n1-2021-mar-abr/como-desenvolver-o-amor-verdadeiro/",
        "fonte": "jw.org",
    },
    "esperança": {
        "versiculo": "Apocalipse 21:4",
        "texto": "Ele enxugará dos seus olhos toda lágrima...",
        "explicacao": "Deus promete um futuro sem dor nem morte.",
        "aplicacao": "Mesmo em dificuldades, mantenha a esperança nas promessas de Jeová.",
        "materia": "https://www.jw.org/pt/biblioteca/revistas/wp20150301/a-esperanca-que-a-biblia-oferece/",
        "fonte": "jw.org",
    },
}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Eu sou seu amigo bíblico.\n"
        "Me envie qualquer pergunta sobre a Bíblia e eu vou tentar te ajudar com base nas publicações das Testemunhas de Jeová."
    )

# Responder perguntas
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text.lower()
    resposta = ""

    for chave, dados in BASE_TEMAS.items():
        if chave in pergunta:
            resposta = (
                f"📖 *Versículo:* {dados['versiculo']}\n"
                f"{dados['texto']}\n\n"
                f"✨ *Explicação:* {dados['explicacao']}\n"
                f"🧭 *Aplicação:* {dados['aplicacao']}\n\n"
                f"📘 *Matéria recomendada:* {dados['materia']}\n"
                f"📚 *Fonte:* {dados['fonte']}\n\n"
                "🙏 Você pode encontrar mais artigos como esse em: https://www.jw.org/pt"
            )
            break

    if not resposta:
        resposta = (
            "Muito obrigado pela sua pergunta! 🙏\n"
            "Ainda não encontrei uma resposta automática para esse tema.\n"
            "Mas você pode buscar diretamente em:\n"
            "🔎 https://www.jw.org/pt ou https://wol.jw.org/pt/wol/h/r5/lp-t\n\n"
            "🙏 Você pode encontrar mais artigos como esse em: https://www.jw.org/pt"
        )

    if resposta.strip():
        await update.message.reply_text(resposta, parse_mode="Markdown")
    else:
        await update.message.reply_text("Desculpe, não encontrei resposta para isso.")

# Inicialização principal
def main():
    PORT = int(os.environ.get("PORT", 8443))
    HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")  # adicione essa variável no Render

    if not HOSTNAME:
        raise ValueError("A variável de ambiente RENDER_EXTERNAL_HOSTNAME não foi definida!")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    # Inicia via webhook (recomendado no Render)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://{HOSTNAME}/{BOT_TOKEN}",
    )

if __name__ == "__main__":
    main()

