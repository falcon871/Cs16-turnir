import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import random

# ========= CONFIG =========
TOKEN = "8436568792:AAGoAkDRgepBfoaTyBYkBEh0rfohuSzHdUo"
ADMIN_ID = 7048705986
# ==========================

bot = telebot.TeleBot(TOKEN)

# ========= DATABASE =========
conn = sqlite3.connect("cs16_turnir.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    nick TEXT
)
""")
conn.commit()
# ============================

tournament = {}

# ========= INLINE MENU =========
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎮 Turnirga qo‘shilish", callback_data="join"),
        InlineKeyboardButton("📋 O‘yinchilar", callback_data="players"),
        InlineKeyboardButton("🏆 G‘oliblar", callback_data="winners"),
    )
    kb.add(
        InlineKeyboardButton("⚙️ Natija (admin)", callback_data="result")
    )
    return kb
# ===============================

# ========= START =========
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🔥 *CS 1.6 TURNIR BOT*\n\n"
        "Quyidagi menyudan foydalaning 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ========= CALLBACKS =========
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "join":
        bot.send_message(call.message.chat.id, "📝 CS nickingizni yozing:")
        bot.register_next_step_handler(call.message, save_nick)

    elif call.data == "players":
        show_players(call.message)

    elif call.data == "result":
        set_result(call.message)

    elif call.data == "winners":
        show_winners(call.message)

# ========= SAVE NICK =========
def save_nick(msg):
    cursor.execute("SELECT 1 FROM players WHERE telegram_id = ?", (msg.from_user.id,))
    if cursor.fetchone():
        bot.send_message(msg.chat.id, "❌ Siz allaqachon ro‘yxatdan o‘tgansiz")
        return

    cursor.execute(
        "INSERT INTO players (telegram_id, nick) VALUES (?, ?)",
        (msg.from_user.id, msg.text)
    )
    conn.commit()
    bot.send_message(msg.chat.id, "✅ Turnirga muvaffaqiyatli qo‘shildingiz!")

# ========= SHOW PLAYERS =========
def show_players(msg):
    cursor.execute("SELECT nick FROM players")
    rows = cursor.fetchall()
    if not rows:
        bot.send_message(msg.chat.id, "📭 Hozircha o‘yinchilar yo‘q")
        return

    text = "🎮 *O‘yinchilar ro‘yxati:*\n"
    text += "\n".join(f"• {r[0]}" for r in rows)
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")

# ========= RESULT =========
def set_result(msg):
    if msg.from_user.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz")
        return

    cursor.execute("SELECT nick FROM players")
    players = [p[0] for p in cursor.fetchall()]
    if len(players) < 2:
        bot.send_message(msg.chat.id, "⚠️ Kamida 2 o‘yinchi kerak")
        return

    winner = random.choice(players)
    players.remove(winner)
    runner = random.choice(players)

    tournament["winner"] = winner
    tournament["runner"] = runner

    bot.send_message(msg.chat.id, "✅ Natija saqlandi!")

# ========= WINNERS =========
def show_winners(msg):
    if not tournament:
        bot.send_message(msg.chat.id, "⏳ Hali natija yo‘q")
        return

    bot.send_message(
        msg.chat.id,
        f"🏆 *TURNIR YAKUNI*\n\n"
        f"🥇 {tournament['winner']} — BOSS\n"
        f"🥈 {tournament['runner']} — PREMIUM",
        parse_mode="Markdown"
    )

# ========= RUN =========
bot.polling(none_stop=True)
