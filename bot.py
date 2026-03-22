import os
import subprocess
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("8761193532:AAG8WFgj26RlCI0yWBZDTsuRzS0uAO2u7-0")

processes = {}

keyboard = ReplyKeyboardMarkup(
    [["🟢 إنشاء البث"],
     ["⛔ إيقاف البث", "📊 حالة البث"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎥 تحكم في البث", reply_markup=keyboard)

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if text == "🟢 إنشاء البث":
        await update.message.reply_text("🔑 أرسل Stream Key:")
        context.user_data["step"] = "key"

    elif context.user_data.get("step") == "key":
        context.user_data["key"] = text
        context.user_data["step"] = "url"
        await update.message.reply_text("📡 أرسل رابط M3U8:")

    elif context.user_data.get("step") == "url":
        key = context.user_data["key"]
        url = text
        rtmp = f"rtmps://live-api-s.facebook.com:443/rtmp/{key}"

        cmd = [
            "ffmpeg",
            "-re",
            "-i", url,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-b:v", "2500k",
            "-c:a", "aac",
            "-f", "flv",
            rtmp
        ]

        process = subprocess.Popen(cmd)
        processes[chat_id] = process

        await update.message.reply_text("🚀 البث بدأ!")

    elif text == "⛔ إيقاف البث":
        if chat_id in processes:
            processes[chat_id].terminate()
            del processes[chat_id]
            await update.message.reply_text("⛔ تم الإيقاف")
        else:
            await update.message.reply_text("❌ لا يوجد بث")

    elif text == "📊 حالة البث":
        if chat_id in processes:
            await update.message.reply_text("🟢 شغال")
        else:
            await update.message.reply_text("🔴 متوقف")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))
    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
