# bot/providers/herosms.py
import requests
from config import HEROSMS_API_KEY

BASE_URL = "https://hero-sms.com/stubs/handler_api.php"

def get_balance():
    """HeroSMS मध्ये किती balance आहे ते सांगतो"""
    params = {
        "api_key": HEROSMS_API_KEY,
        "action": "getBalance"
    }
    r = requests.get(BASE_URL, params=params)
    return r.text.strip()


def get_number(service_code, country=22):
    """
    नवीन नंबर घेतो
    service_code उदाहरण: "wa" (WhatsApp), "tg" (Telegram)
    """
    params = {
        "api_key": HEROSMS_API_KEY,
        "action": "getNumber",
        "service": service_code,
        "country": country
    }
    r = requests.get(BASE_URL, params=params)
    return r.text.strip()


def get_status(order_id):
    """नंबरचा स्टेटस + OTP मिळतो"""
    params = {
        "api_key": HEROSMS_API_KEY,
        "action": "getStatus",
        "id": order_id
    }
    r = requests.get(BASE_URL, params=params)
    return r.text.strip()


def cancel(order_id):
    """नंबर कॅन्सल करतो (refund साठी)"""
    params = {
        "api_key": HEROSMS_API_KEY,
        "action": "setStatus",
        "id": order_id,
        "status": 8  # cancel
    }
    r = requests.get(BASE_URL, params=params)
    return r.text.strip()