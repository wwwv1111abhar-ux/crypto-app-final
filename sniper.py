from telethon import TelegramClient, events, errors
import asyncio
import random
import time

# 🔴 این دو خط رو از سایت my.telegram.org بگیر (اگه نداری، باید بگیری)
API_ID = 1234567 # عدد api_id خودت
API_HASH = 'YOUR_API_HASH_HERE' # متن api_hash خودت

# 🔴 اسم گروه‌هایی که می‌خوای ربات توشون گوش بده
GROUPS_TO_WATCH = [
    'CryptoGroup1',
    'IranCryptoChat',
    'BitcoinPersian'
]

# 🔴 کلماتی که اگه کسی گفت، ربات جواب میده
KEYWORDS = ['سیگنال', 'تحلیل', 'چی بخرم', 'چی بزنم', 'بیت کوین', 'کریپتو', 'تارگت']

# 🔴 متن‌های جواب (ربات رندوم یکی رو میفرسته)
REPLIES = [
    "برای تحلیل دقیق و سیگنال با تارگت و حد ضرر، ربات هوش مصنوعی ما رو استارت کن، ۵ سیگنال اولش رایگانه: @AI_Signal_Crypto_bot 🚀\nکانالمون هم اینه: @CryptoAISignalsGlobal",
    "من از ربات @AI_Signal_Crypto_bot استفاده می‌کنم، تحلیل‌های SMC و سیگنالاش واقعا عالیه. چارتش هم زنده‌ست. پیشنهاد می‌کنم امتحانش کنی 📈\nکانال سیگنالاش: @CryptoAISignalsGlobal",
    "سیگنال‌های روزانه کریپتو با هوش مصنوعی رو توی کانال @CryptoAISignalsGlobal می‌ذارن. برای سیگنال لحظه‌ای هم ربات @AI_Signal_Crypto_bot رو استارت کن. ۵ تاش رایگانه 💎"
]

async def main():
    client = TelegramClient('sniper_session', API_ID, API_HASH)
    await client.start()
    print("🎯 Sniper Bot Started! Listening to groups...")

    replied_users = set()
    group_last_reply = {}

    @client.on(events.NewMessage(chats=GROUPS_TO_WATCH))
    async def handler(event):
        if event.out: return
        text = event.message.text
        if not text: return
        sender_id = event.sender_id
        
        # ضد بن: به هر نفر فقط 1 بار
        if sender_id in replied_users: return

        # ضد بن: هر گروه 12 ساعت فقط 1 بار
        chat_id = event.chat_id
        now = time.time()
        if chat_id in group_last_reply and (now - group_last_reply[chat_id]) < 43200:
            return

        if any(keyword in text for keyword in KEYWORDS):
            try:
                await asyncio.sleep(random.randint(10, 30))
                reply_text = random.choice(REPLIES)
                await event.reply(reply_text)
                
                replied_users.add(sender_id)
                group_last_reply[chat_id] = time.time()
                print(f"✅ Replied in {event.chat.title}")
                
                await asyncio.sleep(1200)
                
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception:
                pass

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
