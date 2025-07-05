import logging
import os
import re
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (caso esteja rodando localmente)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("A variável de ambiente BOT_TOKEN não foi definida!")

# Configura o logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Banco de dados com alguns temas bíblicos
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

# Busca versículo online no wol.jw.org
def buscar_versiculo_online(referencia):
    try:
        partes = referencia.strip().split()
        if len(partes) != 2 or ":" not in partes[1]:
            return None

        livro, cap_vers = partes
        capitulo, versiculo = cap_vers.split(":")

        # Monta URL (por exemplo: https://wol.jw.org/pt/wol/b/r5/lp-t/nwtsty/43/3#v=43:3:16)
        # 43 = João, 3 = capítulo, 16 = versículo
        mapa_livros = {
            "joão": "43", "mateus": "40", "marcos": "41", "lucas": "42",
            "atos": "44", "romanos": "45", "salmos": "19", "gênesis": "1",
            # Adicione outros conforme necessário
        }
        livro_id = mapa_livros.get(livro.lower())
        if not livro_id:
            return None

        url = f"https://wol.jw.org/pt/wol/b/r5/lp-t/nwtsty/{livro_id}/{capitulo}#v={livro_id}:{capitulo}:{versiculo}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        versiculo_tag = soup.find("span", id=f"v{livro_id}:{capitulo}:{versiculo}")

        if versiculo_tag:
            texto = versiculo_tag.get_text(strip=True)
            return f"📖 *{referencia}*: {texto}\n\nFonte: [wol.jw.org]({url})"
        else:
            return "Versículo não encontrado. Tente verificar a referência."
    except Exception as e:
        return f"Erro ao buscar versículo: {e}"

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! 👋 Eu sou seu amigo bíblico.",
    )
    await update.message.reply_text(
        "Você pode me enviar um versículo como `João 3:16` ou perguntar sobre um tema como `amor` ou `esperança`."
    )

# Resposta automática
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text.strip()
    resposta = ""

    # Verifica se é referência tipo "João 3:16"
    if re.match(r"^[A-Za-zçãáéíóú]+ \d+:\d+$", pergunta):
        resposta = buscar_versiculo_online(pergunta)
        await update.message.reply_text(resposta, parse_mode="Markdown")
        return

    # Verifica se é um tema conhecido
    for chave, dados in BASE_TEMAS.items():
        if chave in pergunta.lower():
            resposta = (
                f"📖 *Versículo:* {dados['versiculo']}\n"
                f"{dados['texto']}\n\n"
                f"✨ *Explicação:* {dados['explicacao']}\n"
                f"🧭 *Aplicação:* {dados['aplicacao']}\n\n"
                f"📘 *Matéria recomendada:* {dados['materia']}\n"
                f"📚 *Fonte:* {dados['fonte']}\n\n"
                "🙏 Você pode encontrar mais artigos como esse em: https://www.jw.org/pt"
            )
            await update.message.reply_text(resposta, parse_mode="Markdown")
            return

    # Resposta padrão
    await update.message.reply_text(
        "Desculpe, não consegui encontrar uma resposta para isso. Tente enviar um versículo como `João 3:16` ou um tema bíblico como `amor`.",
        parse_mode="Markdown"
    )

# Inicializa o bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("Bot rodando...")
    application.run_polling()

if __name__ == "__main__":
    main()

