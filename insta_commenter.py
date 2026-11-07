from instagrapi import Client
import time
import random

# 🔴 ۱. سشن آیدی خودت
SESSION_ID = "YOUR_SESSION_ID_HERE" 

# 🔴 ۲. لیست پیج‌های هدف (پیج‌های بزرگ کریپتو)
TARGET_USERNAMES = [
    "cointelegraph",
    "binance",
    "cryptocom",
    "bitcoin",
    "coindesk"
]

# 🔴 ۳. کامنت‌های متنوع
COMMENTS = [
    "تحلیل عالی بود! منم از ربات هوش مصنوعی @CryptoAlpha_2026_bot استفاده می‌کنم، سیگنالاش خیلی دقیقه 🚀",
    "برای کریپتو به نظرم ترکیب تحلیل تکنیکال و هوش مصنوعی جواب میده. کانال @CryptoAISignalsGlobal تحلیل‌های خوبی میذاره 📈",
    "چارت و تارگت‌های رباتتون رو دیدم، واقعا حرفه‌ای بود. ۵ سیگنال رایگانش رو تست کردم، عالی بود 👌",
    "بازار امروز خیلی نوسان داره، حواستون به حد ضرر باشه! ربات @CryptoAlpha_2026_bot تارگت‌های دقیقی میده 💎",
    "سیگنال‌های SMC رو خیلی خوب تحلیل می‌کنه. ممنون از کانال خوبتون @CryptoAISignalsGlobal 🔥",
    "من از سیستم هوش مصنوعی ربات @CryptoAlpha_2026_bot استفاده کردم، تحلیلش برای تایم‌فریم ۱ ساعته دقیق بود 🤖",
    "بهترین راه برای شروع کریپتو، استفاده از سیگنال‌های رایگانه. کانال @CryptoAISignalsGlobal رو پیشنهاد می‌کنم 🎁",
    "تحلیل تایم فریم ۴ ساعته بیت کوین رو دیدم، با تحلیل ربات شما همخوانی داشت! خفنه 🚀",
    "تحلیل عالی بود، ممنون! 🙌",
    "بازار سبزه، امیدوارم همه سود کنن 📈"
]

# 🔴 ۴. کلمات کلیدی (فقط اگه این کلمات توی کپشن پست باشه، کامنت میذاره)
CRYPTO_KEYWORDS = [
    'crypto', 'bitcoin', 'btc', 'eth', 'ethereum', 'blockchain', 'altcoin', 'defi', 'nft', 'web3', 'binance', 'coin', 'token', 'trade', 'market',
    'کریپتو', 'ارز دیجیتال', 'بیت کوین', 'اتریوم', 'بلاکچین', 'سیگنال', 'ترید', 'بازار', 'تحلیل', 'سکه'
]

def login():
    cl = Client()
    try:
        print("🔑 Logging in...")
        cl.login_by_sessionid(SESSION_ID)
        print("✅ Logged in successfully!")
        return cl
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return None

def is_crypto_post(caption):
    if not caption:
        return False
    caption_lower = caption.lower()
    # چک کردن اینکه آیا حداقل یکی از کلمات کلیدی توی کپشن هست یا نه
    return any(keyword in caption_lower for keyword in CRYPTO_KEYWORDS)

def run_campaign(cl):
    total_comments = 10  # تعداد کل کامنت در ۲۴ ساعت
    comments_done = 0
    
    print(f"🎯 Starting Campaign: Target {total_comments} comments.")
    
    while comments_done < total_comments:
        try:
            target = random.choice(TARGET_USERNAMES)
            print(f"\n🔍 Checking @{target}...")
            
            user_id = cl.user_id_from_username(target)
            medias = cl.user_medias(user_id, amount=10) # ۱۰ پست آخر رو چک میکنه
            
            if not medias:
                print(f"❌ No posts found for @{target}. Skipping...")
                continue

            found_valid_post = False
            
            for media in medias:
                # بررسی اینکه آیا پست مربوط به کریپتو هست یا نه
                if is_crypto_post(media.caption_text):
                    print(f"✅ Found a crypto-related post on @{target}!")
                    
                    comment = random.choice(COMMENTS)
                    
                    print(f"💬 Commenting: '{comment[:30]}...'")
                    cl.media_comment(media.id, comment)
                    comments_done += 1
                    print(f"✅ Comment {comments_done}/{total_comments} posted!")
                    
                    found_valid_post = True
                    break # بعد از کامنت گذاشتن برو سراغ پیج بعدی
                else:
                    print("⏭️ Post is not about crypto. Skipping...")
            
            if not found_valid_post:
                print(f"⚠️ No recent crypto posts found on @{target}. Moving to next target.")

            # تاخیر تصادفی بین ۲ تا ۳ ساعت (برای امنیت)
            if comments_done < total_comments:
                wait_time = random.randint(7200, 10800) 
                print(f"⏳ Waiting {wait_time // 60} minutes before next comment...")
                time.sleep(wait_time)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("⏳ Waiting 5 minutes before trying again...")
            time.sleep(300)

if __name__ == "__main__":
    client = login()
    if client:
        run_campaign(client)
