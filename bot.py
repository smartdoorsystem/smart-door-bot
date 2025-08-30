from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

# 🔑 حط التوكن متاع البوت هنا
BOT_TOKEN = "8325912903:AAHYb-xLVI-JXWl3dc6_P8x2WwpqA_siA3g"

# السؤال والإجابة
QUESTION = "what's the Smart door system comniection smart door system - communicate group password?"
CORRECT_ANSWER = "19201"
TIME_LIMIT = 30  # بالثواني

# نخزن مؤقت العضو الجديد
pending_users = {}

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        chat_id = update.message.chat_id
        user_id = member.id

        # نسأل العضو الجديد
        await context.bot.send_message(chat_id, f"Welcome {member.first_name}! {QUESTION}\nYou have {TIME_LIMIT} seconds to answer.")

        # ننتظر الإجابة
        task = asyncio.create_task(kick_if_no_answer(chat_id, user_id, context))
        pending_users[user_id] = {"task": task, "chat_id": chat_id}

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id in pending_users:
        if text == CORRECT_ANSWER:
            await update.message.reply_text("✅ Correct! You may stay in the group.")
            pending_users[user_id]["task"].cancel()
            del pending_users[user_id]
        else:
            await update.message.reply_text("❌ Wrong answer! You will be removed.")
            chat_id = pending_users[user_id]["chat_id"]
            await context.bot.ban_chat_member(chat_id, user_id)
            del pending_users[user_id]

async def kick_if_no_answer(chat_id, user_id, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(TIME_LIMIT)
    if user_id in pending_users:
        await context.bot.send_message(chat_id, "⏰ Time is up! Removing user.")
        await context.bot.ban_chat_member(chat_id, user_id)
        del pending_users[user_id]

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

