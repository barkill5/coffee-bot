import os
import csv
import asyncio
import threading
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

def load_menu():
    menu = []
    with open('menu.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            menu.append(row)
    return menu

MENU = load_menu()

def menu_to_text(items):
    if not items:
        return "Ничего не найдено"
    lines = ["Меню:"]
    for item in items:
        lines.append(f"{item['item']} - {item['price']}")
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот кофейни. Напиши /menu")

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = menu_to_text(MENU)
    await update.message.reply_text(text)

async def price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    found_items = []
    for item in MENU:
        if item['item'].lower() in user_text:
            found_items.append(item)
    
    if found_items:
        await update.message.reply_text(menu_to_text(found_items))
    else:
        await menu_cmd(update, context)

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app_flask.run(host='0.0.0.0', port=port)

async def run_bot():
    print("1. Создаю Application...")
    app = Application.builder().token(TOKEN).build()
    print("2. Добавляю хендлеры...")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'(?i)(цена|сколько стоит|прайс|цены)'), 
        price_handler
    ))
    print("3. Starting bot...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("4. Bot is polling!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())