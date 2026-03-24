
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot activo ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import uuid, os

from config import *
from downloader import download_file
from compressor import compress_and_split
from uploader import upload_file
from queue_manager import queue, start_workers
from utils import *

from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot activo ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# START
@bot.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user.username

    if user == ADMIN_USERNAME:
        await message.reply("🚀 Panel Admin", reply_markup=admin_panel_markup())
    elif is_allowed(user):
        await message.reply("🚀 Tienes acceso al bot")
    else:
        await message.reply(
            "⛔ No tienes acceso al bot. Solo puedes usarlo si el admin te da acceso.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Contactar Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
            ])
        )

# BOTONES ADMIN
@bot.on_callback_query()
async def callbacks(client, cb: CallbackQuery):
    user = cb.from_user.username
    if user != ADMIN_USERNAME:
        return await cb.answer("No autorizado", True)

    if cb.data == "admin_list":
        users = get_users()
        text = "\n".join(f"@{u}" for u in users) or "Vacío"
        await cb.message.reply(text)

    elif cb.data == "admin_add":
        tasks[user+"_add"] = True
        await cb.message.reply("Envía @usuario")

    elif cb.data == "admin_del":
        tasks[user+"_del"] = True
        await cb.message.reply("Envía @usuario")

    elif cb.data.startswith("cancel_"):
        tid = cb.data.split("_")[1]
        if tid in tasks:
            tasks[tid]["cancel"] = True
        await cb.answer("Cancelando...")

# RESPUESTAS ADMIN
@bot.on_message(filters.text)
async def admin_text(client, message):
    user = message.from_user.username

    if tasks.get(user+"_add"):
        u = message.text.replace("@","")
        add_user(u)
        await message.reply(f"✅ @{u} añadido")
        tasks.pop(user+"_add", None)

    elif tasks.get(user+"_del"):
        u = message.text.replace("@","")
        remove_user(u)
        await message.reply(f"❌ @{u} eliminado")
        tasks.pop(user+"_del", None)

# ARCHIVOS
@bot.on_message(filters.document | filters.video | filters.audio)
async def handle(client, message):
    user = message.from_user.username

    if user != ADMIN_USERNAME and not is_allowed(user):
        return await message.reply("⛔ No tienes acceso")

    status = await message.reply("📥 En cola...")
    task_id = uuid.uuid4().hex

    async def task():
        tasks[task_id] = {"cancel": False}

        def cancel():
            return tasks[task_id]["cancel"]

        file = await client.get_file(message.document.file_id)
        url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        name = message.document.file_name

        async def prog(p,s,e):
            if cancel(): raise Exception()
            await status.edit(f"⬇️\n{get_progress_text(p,s,e)}", reply_markup=get_cancel_markup(task_id))

        path = await download_file(url, name, prog)

        parts = compress_and_split(path)

        links = []
        for i, part in enumerate(parts):
            if cancel(): raise Exception()
            await status.edit(f"☁️ {int(i/len(parts)*100)}%", reply_markup=get_cancel_markup(task_id))
            link = await upload_file(f"file_{uuid.uuid4().hex}", part)
            links.append(link)
            os.remove(part)

        os.remove(path)

        txt = name.split(".")[0]+".txt"
        with open(txt,"w") as f:
            for l in links: f.write(l+"\n")

        await client.send_document(message.chat.id, txt)
        os.remove(txt)
        await status.delete()

    await queue.put((task, []))

bot.loop.create_task(start_workers())
bot.run()
