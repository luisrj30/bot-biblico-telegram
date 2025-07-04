import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Carrega variáveis do arquivo .env (funciona localmente)
load_dotenv()

# Pega o token da variável de ambiente chamada BOT_TOKEN
BOT_TOKEN = os.getenv("7855633786:AAHH0nTE2Rk4RJEuXf0i7LM7YO9q9V3KZ4o")

# Verifica se o token foi carregado corretamente
if not BOT_TOKEN:
    raise ValueError("A variável de ambiente BOT_TOKEN não foi definida!")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

BASE_TEMAS = {
    "amor": {
        "versiculo": "1 Coríntios 13:4-7",
        "texto": "O amor é paciente e bondoso. O amor não é ciumento, não se gaba, não é orgulhoso...",
        "explicacao": "O texto mostra como o amor verdadeiro se comporta. Não é apenas um sentimento, mas uma escolha diária de agir com bondade e paciência.",
        "aplicacao": "Podemos aplicar esse texto sendo pacientes com os outros, mesmo quando estão errados.",
        "materia": "https://www.jw.org/pt/biblioteca/revistas/a-despertai-n1-2021-mar-abr/como-desenvolver-o-amor-verdadeiro/",
        "fonte": "jw.org",
    },
    "esperança": {
        "versiculo": "Apocalipse 21:4",
        "texto": "Ele enxugará dos seus olhos toda lágrima, e não haverá mais morte, nem tristeza, nem clamor, nem dor...",
        "explicacao": "Esse versículo mostra a promessa de Deus para um futuro sem sofrimento.",
        "aplicacao": "Mesmo em tempos difíceis, podemos manter a esperança de que Jeová cumprirá suas promessas.",
        "materia": "https://www.jw.org/pt/biblioteca/revistas/wp20150301/a-esperanca-que-a-biblia-oferece/",
        "fonte": "jw.org",
    },
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Eu sou seu amigo bíblico.\n"
        "Me envie qualquer pergunta sobre a Bíblia e eu vou tentar te ajudar com base nas publicações das Testemunhas de Jeová."
    )


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text.lower()
    resposta = ""

    for chave, dados in BASE_TEMAS.items():
        if chave in pergunta:
            resposta = f"📖 *Versículo:* {dados['versiculo']}\n"
            resposta += f"{dados['texto']}\n\n"
            resposta += f"✨ *Explicação:* {dados['explicacao']}\n"
            resposta += f"🧭 *Aplicação:* {dados['aplicacao']}\n\n"
            resposta += f"📘 *Matéria recomendada:* {dados['materia']}\n"
            resposta += f"📚 *Fonte:* {dados['fonte']}\n\n"
            resposta += "🙏 Você pode encontrar mais artigos como esse em: https://www.jw.org/pt"
            break

    if not resposta:
        resposta = (
            "Muito obrigado pela sua pergunta! 🙏\n"
            "Por enquanto, não encontrei uma resposta automática para esse tema.\n"
            "Mas você pode buscar diretamente em https://www.jw.org/pt ou https://wol.jw.org/pt/wol/h/r5/lp-t\n\n"
            "🙏 Você pode encontrar mais artigos como esse em: https://www.jw.org/pt"
        )

    await update.message.reply_text(resposta, parse_mode="Markdown")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot rodando...")
    application.run_polling()


if __name__ == "__main__":
    main()
