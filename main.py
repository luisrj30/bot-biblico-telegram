import logging
import os
import re
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("A variável de ambiente BOT_TOKEN não foi definida!")

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Função para buscar o versículo no site wol.jw.org
def buscar_versiculo(referencia: str):
    referencia_formatada = referencia.strip().replace(" ", "+")
    url_busca = f"https://wol.jw.org/pt/wol/lv/r5/lp-t?q={referencia_formatada}"

    try:
        resposta = requests.get(url_busca)
        soup = BeautifulSoup(resposta.text, 'html.parser')

        link_resultado = soup.select_one(".resultTitle a")
        if not link_resultado:
            return None, None, None, "Texto não encontrado. Verifique a referência."

        url_texto = "https://wol.jw.org" + link_resultado["href"]
        pagina = requests.get(url_texto)
        soup_texto = BeautifulSoup(pagina.text, "html.parser")

        texto_biblico = soup_texto.select_one(".b").get_text(strip=True) if soup_texto.select_one(".b") else None
        explicacao = soup_texto.select_one(".sb").get_text(strip=True) if soup_texto.select_one(".sb") else "Explicação não encontrada."
        aplicacao = "Pense em como esse texto pode se aplicar na sua vida. Ore a Jeová pedindo sabedoria para pôr isso em prática."

        return texto_biblico, explicacao, aplicacao, url_texto
    except Exception as e:
        return None, None, None, f"Erro ao buscar versículo: {e}"

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Eu sou seu amigo bíblico.\n"
        "Envie um versículo como 'João 3:16' ou 'Provérbios 14:16' e eu trarei o texto, uma explicação e como aplicá-lo na vida prática!"
    )

# Comando para tratar mensagens
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text.strip()
    if not pergunta:
        await update.message.reply_text("❗ Por favor, envie uma pergunta ou referência bíblica.")
        return

    texto, explicacao, aplicacao, link = buscar_versiculo(pergunta)

    if texto:
        resposta = (
            f"📖 *Texto:* {texto}\n\n"
            f"✨ *Explicação:* {explicacao}\n"
            f"🧭 *Aplicação:* {aplicacao}\n\n"
            f"🔗 *Leia mais:* {link}\n\n"
            "🙏 Você pode encontrar mais artigos como esse em: https://www.jw.org/pt"
        )
    else:
        resposta = (
            f"❗ {link}\n\n"
            "Você pode buscar diretamente em: https://wol.jw.org/pt/wol/h/r5/lp-t"
        )

    await update.message.reply_text(resposta, parse_mode="Markdown")

# Função principal
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Bot rodando...")
    application.run_polling()

if __name__ == "__main__":
    main()


