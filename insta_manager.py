from instagrapi import Client
import time
import random

# 🔴 سشن آیدی خودت (همونی که از مرورگر گرفتی)
SESSION_ID = "YOUR_SESSION_ID_HERE" 

# 🔴 اسم فایل عکسی که می‌خوای پست کنی (لوگوی ربات)
IMAGE_PATH = "logo.jpg" 

CAPTION = """
🚀 سیگنال‌های روزانه کریپتو با هوش مصنوعی!
📈 تحلیل دقیق، تارگت، حد ضرر و چارت زنده.
🎁 ۵ سیگنال اول کاملاً رایگان!

👇 برای دریافت سیگنال‌های رایگان، ربات تلگرام ما رو استارت کن (لینک در بیو پیج):
#کریپتو #ارز_دیجیتال #بیت_کوین #سیگنال_ارز #ترید #crypto #bitcoin
"""

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

def post_photo(cl):
    try:
        print("📤 Uploading Photo Post...")
        media = cl.photo_upload(path=IMAGE_PATH, caption=CAPTION)
        print(f"🎉 Post published! Media ID: {media.pk}")
    except Exception as e:
        print(f"❌ Error posting photo: {e}")

def post_story(cl):
    try:
        print("📸 Uploading Story...")
        cl.photo_upload_to_story(path=IMAGE_PATH)
        print("🎉 Story published successfully!")
    except Exception as e:
        print(f"❌ Error posting story: {e}")

def post_comment(cl, target_username, comment_text):
    try:
        print(f"💬 Finding latest post of @{target_username}...")
        user_id = cl.user_id_from_username(target_username)
        medias = cl.user_medias(user_id, amount=1)
        
        if not medias:
            print("❌ No posts found for this user.")
            return

        media_id = medias[0].id
        # تاخیر تصادفی قبل از کامنت (بین 10 تا 30 ثانیه) که شبیه ربات نباشه
        wait_time = random.randint(10, 30)
        print(f"⏳ Waiting {wait_time} seconds before commenting...")
        time.sleep(wait_time)
        
        cl.media_comment(media_id, comment_text)
        print(f"✅ Commented on @{target_username}'s post successfully!")
    except Exception as e:
        print(f"❌ Error commenting: {e}")

if __name__ == "__main__":
    client = login()
    if client:
        print("\n🤖 Choose an action:")
        print("1. Post Photo")
        print("2. Post Story")
        print("3. Comment on a specific user's latest post")
        
        choice = input("Enter number (1/2/3): ")
        
        if choice == '1':
            post_photo(client)
        elif choice == '2':
            post_story(client)
        elif choice == '3':
            target = input("Enter username to comment on (without @): ")
            comment = input("Enter your comment: ")
            post_comment(client, target, comment)
        else:
            print("Invalid choice.")
