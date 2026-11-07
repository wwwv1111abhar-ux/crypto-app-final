import json, os, time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "os.getenv("BOT_TOKEN")"
PRIVATE_CHANNEL_ID = -1004212871363 # آیدی کانال فارکس
USERS_FILE = "forex_users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f: return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    
    if user_id in users and users[user_id]["premium_until"] > time.time():
        await update.message.reply_text("✅ You are a Premium Member! Click below to get your invite link.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Get Channel Link", callback_data="get_link")]
        ]))
    else:
        keyboard = [
            [InlineKeyboardButton("1 Month - 100 Stars", callback_data="plan_30")],
            [InlineKeyboardButton("3 Months - 250 Stars", callback_data="plan_90")],
            [InlineKeyboardButton("6 Months - 450 Stars", callback_data="plan_180")],
            [InlineKeyboardButton("1 Year - 800 Stars", callback_data="plan_365")]
        ]
        await update.message.reply_text(
            "🌟 **Welcome to Forex & Gold VIP Signals!**\n\n"
            "To get access to our exclusive gold and forex signals, please choose a subscription plan below:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def buy_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_days = query.data.split("_")[1]
    prices = {"30": 100, "90": 250, "180": 450, "365": 800}
    
    await context.bot.send_invoice(
        chat_id=query.message.chat_id, title=f"VIP Access ({plan_days} Days)", description="Exclusive Forex & Gold Signals",
        payload=f"sub_{plan_days}", provider_token="", currency="XTR", prices=[LabeledPrice(label="VIP Subscription", amount=prices[plan_days])]
    )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    payload = update.message.successful_payment.invoice_payload
    days = int(payload.split("_")[1])
    
    users = load_users()
    current_until = users.get(user_id, {}).get("premium_until", time.time())
    new_until = max(time.time(), current_until) + (days * 86400)
    
    users[user_id] = {"premium_until": new_until}
    save_users(users)
    
    try:
        link = await context.bot.create_chat_invite_link(chat_id=PRIVATE_CHANNEL_ID, member_limit=1)
        await update.message.reply_text(
            f"✅ **Payment Successful!**\nYour subscription is active until {datetime.fromtimestamp(new_until).strftime('%Y-%m-%d')}.\n\n"
            f"Click here to join the VIP Channel:\n{link.invite_link}"
        )
    except Exception as e:
        await update.message.reply_text(f"Payment received, but error creating link: {e}")

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        link = await context.bot.create_chat_invite_link(chat_id=PRIVATE_CHANNEL_ID, member_limit=1)
        await query.message.reply_text(f"Here is your one-time invite link:\n{link.invite_link}")
    except Exception as e:
        await query.message.reply_text(f"Error: {e}")

async def expire_users(context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    now = time.time()
    for uid, data in list(users.items()):
        if data["premium_until"] < now:
            try:
                await context.bot.ban_chat_member(chat_id=PRIVATE_CHANNEL_ID, user_id=int(uid))
                await context.bot.unban_chat_member(chat_id=PRIVATE_CHANNEL_ID, user_id=int(uid))
                del users[uid]
            except Exception:
                pass
    save_users(users)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy_plan, pattern="^plan_"))
    app.add_handler(CallbackQueryHandler(get_link, pattern="^get_link$"))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    
    job_queue = app.job_queue
    job_queue.run_repeating(expire_users, interval=86400, first=10)
    
    print("Forex VIP Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
