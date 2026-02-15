# payments/razorpay_gateway.py
import razorpay
from dotenv import load_dotenv
import os

load_dotenv()  # .env फाईल लोड करतो

# Razorpay क्लायंट तयार कर
client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

def create_order(amount_in_rupees: float, user_id: int = None):
    """
    Razorpay वर ऑर्डर तयार करते.
    amount_in_rupees → 100 म्हणजे ₹100
    user_id → notes मध्ये सेव्ह होईल (webhook साठी उपयोगी)
    """
    try:
        data = {
            "amount": int(amount_in_rupees * 100),  # paise मध्ये (रुपय × 100)
            "currency": "INR",
            "payment_capture": 1,  # ऑटो कॅप्चर
            "notes": {
                "user_id": str(user_id) if user_id else "unknown"
            }
        }
        order = client.order.create(data=data)
        return {
            "success": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }