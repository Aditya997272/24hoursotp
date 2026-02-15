# config.py
# हे फाईल फक्त variables ची structure आणि .env लोडिंगसाठी आहे
# API keys किंवा secrets इथे कधीही हार्डकोड करू नका – .env किंवा Render Environment मधून घ्या

import os
from dotenv import load_dotenv

# .env फाईल लोड कर (लोकल टेस्टिंगसाठी)
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "5607965245"))  # default तुझा ID
YOUR_CHANNEL_ID = os.getenv("YOUR_CHANNEL_ID", "@hoursotp24")

# HeroSMS (OTP provider)
HEROSMS_API_KEY = os.getenv("HEROSMS_API_KEY")
HEROSMS_BASE_URL = "https://hero-sms.com/stubs/handler_api.php"

# Razorpay (Payment gateway)
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

# Database (MySQL / XAMPP)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "db_24hoursotp")

# Business Logic
MINIMUM_RECHARGE = float(os.getenv("MINIMUM_RECHARGE", "30.0"))
REFERRAL_BONUS = float(os.getenv("REFERRAL_BONUS", "10.0"))

# Print to check (deploy logs साठी उपयुक्त – production मध्ये काढून टाका)
if __name__ == "__main__":
    print("Config loaded successfully:")
    print(f"  BOT_TOKEN: {'Set' if BOT_TOKEN else 'Missing'}")
    print(f"  ADMIN_USER_ID: {ADMIN_USER_ID}")
    print(f"  HEROSMS_API_KEY: {'Set' if HEROSMS_API_KEY else 'Missing'}")
    print(f"  RAZORPAY_KEY_ID: {'Set' if RAZORPAY_KEY_ID else 'Missing'}")