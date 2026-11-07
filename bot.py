import json
import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "https://superlative-tiramisu-296a85.netlify.app"
BOT_USERNAME = "AI_Signal_Crypto_bot" 
ADMIN_ID = 9256885133 
CHANNEL_USERNAME = "@CryptoAISignalsGlobal" # 🔴 یوزرنیم کانالت

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f: return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f)

def get_user(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"premium_until": 0, "signals": 5}
        save_users(users)
    return users[uid]

def update_user(user_id, data):
    users = load_users()
    uid = str(user_id)
    if uid not in users: users[uid] = {"premium_until": 0, "signals": 5}
    users[uid].update(data)
    save_users(users)

# تابع چک کردن عضویت در کانال
async def is_user_joined(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    # اگه ادمین بود، مستقیم بره تو
    if user_id == ADMIN_ID:
        update_user(user_id, {"premium_until": 9999999999})
        reply_keyboard = [[KeyboardButton("🏠 Main Menu")]]
        reply_markup_persistent = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, is_persistent=True)
        
        await update.message.reply_text(
            "👑 **Welcome Admin!**\nYou have unlimited access to all features.",
            reply_markup=reply_markup_persistent
        )
        await update.message.reply_text(
            "Click below to open the app:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Open AI App (Admin)", web_app=WebAppInfo(url=f"{BASE_URL}/?uid={user_id}&until=9999999999&admin=true"))]
            ])
        )
        return

    # چک کردن عضویت در کانال برای کاربرای عادی
    joined = await is_user_joined(user_id, context)
    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Our Channel First", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ I Joined, Let Me In", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "⚠️ **Access Denied!**\n\nTo use this bot and get AI signals, you must join our official channel first.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # لینک دعوت (رفرال)
    if context.args and context.args[0].startswith("ref_"):
        referrer_id = context.args[0].replace("ref_", "")
        if referrer_id != str(user_id):
            referrer = get_user(referrer_id)
            update_user(referrer_id, {"signals": referrer["signals"] + 3})
            try: await context.bot.send_message(chat_id=referrer_id, text="🎉 Someone joined using your link! You earned 3 free signals.")
            except: pass

    current_time = int(time.time())
    is_premium = user.get("premium_until", 0) > current_time
    premium_until = user.get("premium_until", 0)
    web_app_url = f"{BASE_URL}/?uid={user_id}&until={premium_until}"
    
    keyboard = [
        [InlineKeyboardButton("🚀 Open AI App", web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton("🎁 Invite Friends (+3 Signals)", callback_data="invite")],
        [InlineKeyboardButton("⭐ Premium Plans (Save more!)", callback_data="show_plans")],
        [InlineKeyboardButton("💎 Buy 1 Signal (10 Stars)", callback_data="buy_single")]
    ]
    
    status_text = "👑 Premium Active" if is_premium else f"🆓 Free Account ({user['signals']} signals left)"
    
    reply_keyboard = [[KeyboardButton("🏠 Main Menu")]]
    reply_markup_persistent = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, is_persistent=True)
    
    await update.message.reply_text(
        "Main Menu loaded! Use the button below anytime you need to return.",
        reply_markup=reply_markup_persistent
    )
    await update.message.reply_text(
        f"Welcome to Crypto AI! 🧠\n\nStatus: {status_text}\n\nClick below to start trading.", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    joined = await is_user_joined(user_id, context)
    if joined:
        await query.message.delete()
        await start(update, context)
    else:
        await query.answer("❌ You haven't joined the channel yet!", show_alert=True)

async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("1 Month - 100 Stars", callback_data="plan_30")],
        [InlineKeyboardButton("3 Months - 250 Stars (Save 17%)", callback_data="plan_90")],
        [InlineKeyboardButton("6 Months - 450 Stars (Save 25%)", callback_data="plan_180")],
        [InlineKeyboardButton("1 Year - 800 Stars (Best Value!)", callback_data="plan_365")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]
    ]
    await query.message.reply_text(
        "⭐ **Choose Your Premium Plan**", 
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def buy_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan = query.data.split("_")[1] 
    prices = {"30": 100, "90": 250, "180": 450, "365": 800}
    titles = {"30": "1 Month Premium", "90": "3 Months Premium", "180": "6 Months Premium", "365": "1 Year Premium"}
    await context.bot.send_invoice(
        chat_id=query.message.chat_id, title=titles[plan], description=f"Unlimited AI Signals for {plan} days",
        payload=f"premium_{plan}", provider_token="", currency="XTR", prices=[LabeledPrice(label=titles[plan], amount=prices[plan])]
    )

async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{query.from_user.id}"
    await query.message.reply_text(f"🎁 **Invite & Earn**\n\nShare this link. For every friend, you get **3 free signals**!\n\n`{ref_link}`", parse_mode="Markdown")

async def buy_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await context.bot.send_invoice(
        chat_id=query.message.chat_id, title="1 AI Signal", description="Get 1 more signal",
        payload="single_10", provider_token="", currency="XTR", prices=[LabeledPrice(label="1 Signal", amount=10)]
    )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    payload = update.message.successful_payment.invoice_payload
    user = get_user(user_id)
    
    if payload.startswith("premium_"):
        days = int(payload.split("_")[1])
        current_until = user.get("premium_until", 0)
        start_time = max(int(time.time()), current_until)
        new_until = start_time + (days * 24 * 60 * 60)
        update_user(user_id, {"premium_until": new_until})
        await update.message.reply_text(
            f"👑 **Premium Activated for {days} Days!**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Open Premium App", web_app=WebAppInfo(url=f"{BASE_URL}/?uid={user_id}&until={new_until}"))]])
        )
    elif payload == "single_10":
        update_user(user_id, {"signals": user["signals"] + 1})
        await update.message.reply_text(
            "✅ You bought 1 extra signal!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Open App", web_app=WebAppInfo(url=f"{BASE_URL}/?uid={user_id}&until={user.get('premium_until', 0)}"))]])
        )

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data == "show_plans": await show_plans(update, context)
    elif data.startswith("plan_"): await buy_plan(update, context)
    elif data == "buy_single": await buy_single(update, context)
    elif data == "invite": await invite(update, context)
    elif data == "back_to_start": await start(update, context)
    elif data == "check_join": await check_join(update, context)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Main Menu":
        await start(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, paid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
