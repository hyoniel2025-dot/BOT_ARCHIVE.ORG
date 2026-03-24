from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json, os

tasks = {}
USERS_FILE = "users.json"

# ---- usuarios ----
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def add_user(username):
    users = load_users()
    if username not in users:
        users.append(username)
        save_users(users)
        return True
    return False

def remove_user(username):
    users = load_users()
    if username in users:
        users.remove(username)
        save_users(users)
        return True
    return False

def get_users():
    return load_users()

def is_allowed(username):
    return username in load_users()

# ---- UI ----
def get_progress_text(percent, speed=0, eta=0):
    bar = "█" * (percent // 10) + "░" * (10 - percent // 10)
    speed_mb = speed / (1024 * 1024)
    eta_text = f"{int(eta)}s" if eta > 0 else "..."
    return f"[{bar}] {percent}%\n⚡ {speed_mb:.2f} MB/s\n⏳ {eta_text}"

def get_cancel_markup(task_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{task_id}")]
    ])

def admin_panel_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Añadir usuario", callback_data="admin_add")],
        [InlineKeyboardButton("➖ Eliminar usuario", callback_data="admin_del")],
        [InlineKeyboardButton("📋 Lista de usuarios", callback_data="admin_list")]
    ])