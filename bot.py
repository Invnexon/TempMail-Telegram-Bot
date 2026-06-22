import logging
import sqlite3
import requests
import os
from aiogram import Bot, Dispatcher, executor, types

# Token direct variable se le raha hai
API_TOKEN = '8863248333:AAHCxCfU3P6JNY2Dlh6dEB_m8WqwC91lQLg' 
ADMIN_ID = 7422190601

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Database Setup
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER)')
conn.commit()

# Commands
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    cursor.execute('INSERT OR IGNORE INTO users (id, balance) VALUES (?, ?)', (message.from_user.id, 0))
    conn.commit()
    await message.reply("Welcome! Use /generate (costs 1 credit) or /check.")

@dp.message_handler(commands=['add'])
async def add_credits(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        args = message.text.split()
        user_id, amount = int(args[1]), int(args[2])
        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
        conn.commit()
        await message.reply(f"User {user_id} ko {amount} credits add kar diye.")

@dp.message_handler(commands=['generate'])
async def generate(message: types.Message):
    cursor.execute('SELECT balance FROM users WHERE id = ?', (message.from_user.id,))
    data = cursor.fetchone()
    if data and data[0] > 0:
        url = "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1"
        email = requests.get(url).json()[0]
        cursor.execute('UPDATE users SET balance = balance - 1 WHERE id = ?', (message.from_user.id,))
        conn.commit()
        await message.reply(f"Generated: `{email}`\nMail check karne ke liye: /check {email}")
    else:
        await message.reply("Balance nahi hai!")

@dp.message_handler(commands=['check'])
async def check_mail(message: types.Message):
    try:
        email = message.text.split()[1]
        user, domain = email.split('@')
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={user}&domain={domain}"
        messages = requests.get(url).json()
        if not messages:
            await message.reply("Inbox khali hai.")
        else:
            for msg in messages:
                await message.reply(f"Mail mila!\nFrom: {msg['from']}\nSubject: {msg['subject']}")
    except:
        await message.reply("Format: /check email@domain.com")

# executor.start_polling(dp, skip_updates=True) # Ise hata dein

# Iski jagah Webhook setup karein (FastAPI ke saath):
from aiogram import Bot, Dispatcher

# ... (baaki code)

# bot.py ke last mein
if __name__ == "__main__":
    import uvicorn
    # Port ko 8080 set karein
    uvicorn.run(app, host="0.0.0.0", port=8080)
