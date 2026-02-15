# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # .env फाईल लोड करतो

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))
YOUR_CHANNEL_ID = os.getenv("YOUR_CHANNEL_ID")

HEROSMS_API_KEY = os.getenv("HEROSMS_API_KEY")

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = os.getenv("DB_NAME", "db_24hoursotp")

MINIMUM_RECHARGE = float(os.getenv("MINIMUM_RECHARGE", 30.0))
REFERRAL_BONUS = float(os.getenv("REFERRAL_BONUS", 10.0))