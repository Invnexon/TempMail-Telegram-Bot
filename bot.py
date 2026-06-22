import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import random
import sqlite3

# --- CONFIG ---
API_TOKEN = '8863248333:AAHCxCfU3P6JNY2Dlh6dEB_m8WqwC91lQLg'
ADMIN_ID = 7422190601  # Aapki Chat ID
DOMAINS = ["sudiphub.com", "sudip.pro"]
INDIAN_NAMES = ["arjun", "priya", "rohan", "sneha", "vikram", "anjali", "amit", "pooja"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- DATABASE ---
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
conn.commit()

# --- COMMANDS ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)', (user_id,))
    conn.commit()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    balance = cursor.fetchone()[0]
    await message.reply(f"Welcome! Aapka current balance: {balance} credits.\nCommands: /generate, /pay")

@dp.message_handler(commands=['generate'])
async def generate(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()
    balance = data[0] if data else 0
    
    if balance < 10:
        await message.reply("Balance kam hai! /pay karke points add karwayein.")
    else:
        cursor.execute('UPDATE users SET balance = balance - 10 WHERE user_id = ?', (user_id,))
        conn.commit()
        email = f"{random.choice(INDIAN_NAMES)}{random.randint(100, 999)}@{random.choice(DOMAINS)}"
        await message.reply(f"Generated Email: `{email}`\nRemaining: {balance - 10}", parse_mode="Markdown")

@dp.message_handler(commands=['pay'])
async def pay(message: types.Message):
    await message.reply("UPI: `paytm.s17yd0l@pty`\n100 Rs = 100 Credits.\nPayment karke screenshot Admin ko bhejein.")

@dp.message_handler(commands=['add'])
async def add_credit(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("Ye command sirf Admin ke liye hai.")
    args = message.get_args().split()
    if len(args) == 2:
        cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (int(args[1]), int(args[0])))
        conn.commit()
        await message.reply(f"User {args[0]} ko {args[1]} credits add kar diye.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)