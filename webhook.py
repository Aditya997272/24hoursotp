# webhook.py (रूट फोल्डरमध्ये)
from flask import Flask, request, jsonify
import hmac
import hashlib
from config import RAZORPAY_KEY_SECRET
import db  # तुझा DB फंक्शन import कर

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def razorpay_webhook():
    payload = request.data
    signature = request.headers.get('X-Razorpay-Signature')

    # Signature verify (सुरक्षिततेसाठी)
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        return jsonify({"status": "invalid signature"}), 400

    data = request.json
    if data['event'] == 'payment.captured':
        amount = data['payload']['payment']['entity']['amount'] / 100  # paise to rupees
        user_id = int(data['payload']['payment']['entity']['notes'].get('user_id', 0))
        
        if user_id > 0:
            db.update_balance(user_id, amount, "CREDIT", "Razorpay Recharge")
            print(f"[Webhook] Balance credited ₹{amount} to user {user_id}")
            # Telegram bot ने user ला मेसेज पाठवायचा असेल तर context/bot instance हवं (पुढे जोडू)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render साठी port 10000