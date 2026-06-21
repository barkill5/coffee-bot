from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd

TOKEN = "8946010669:AAFSfmDf4vsxRElvmYc3R9ckZ08x9uiVJp4"

# Грузим меню 1 раз при старте
df = pd.read_csv('menu.csv')

def df_to_text(dataframe):
    """Превращаем DataFrame в красивый текст для Telegram"""
    lines = ["Меню:"]
    for _, row in dataframe.iterrows():
        lines.append(f"{row['item']} - {row['price']}")
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот кофейни. Напиши /menu")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = df_to_text(df)
    await update.message.reply_text(text)

async def price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    
    # Ищем какой напиток упомянул пользователь
    found_items = []
    for item_name in df['item']:
        if item_name.lower() in user_text:
            found_items.append(item_name)
    
    if found_items:
        # Нашли конкретные напитки - показываем только их
        filtered = df[df['item'].isin(found_items)]
        await update.message.reply_text(df_to_text(filtered))
    else:
        # Просто спросили "цена" без уточнения - кидаем всё меню
        await menu(update, context)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(MessageHandler(
    filters.TEXT & filters.Regex(r'(?i)(цена|сколько стоит|прайс|цены)'), 
    price_handler
))

app.run_polling()