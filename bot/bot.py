import logging
import asyncio
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import BOT_TOKEN, ADMIN_USER_ID
import db
from providers.herosms import get_number, get_status, cancel
from payments.razorpay_gateway import create_order as razorpay_create_order

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= OTP POLLING =================
async def wait_for_otp(context: ContextTypes.DEFAULT_TYPE, user_id: int, activation_id: str, price: float, service_name: str):
    for _ in range(24):  # 2 minutes
        await asyncio.sleep(5)
        status = get_status(activation_id)

        if "STATUS_OK" in status:
            otp = status.split(":")[1]
            await context.bot.send_message(
                user_id,
                f"✅ OTP RECEIVED!\n🔢 `{otp}`\n📱 {service_name}",
                parse_mode="Markdown"
            )
            db.update_order_status(activation_id, "OTP_RECEIVED", otp)
            return

    cancel(activation_id)
    db.update_balance(user_id, price, "CREDIT", "Refund - Timeout")
    await context.bot.send_message(user_id, "⏳ OTP Timeout. Refunded.")

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    db.add_or_get_user(uid)

    if db.is_user_blocked(uid):
        await update.message.reply_text("🚫 You are blocked.")
        return

    if uid == ADMIN_USER_ID:
        kb = [
            [KeyboardButton("👥 Users"), KeyboardButton("🛠 Servers")],
            [KeyboardButton("📢 Broadcast")]
        ]
        await update.message.reply_text(
            "👑 ADMIN PANEL",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )
    else:
        kb = [
            [KeyboardButton("🛒 Buy Number"), KeyboardButton("💰 Wallet")],
            [KeyboardButton("📜 History"), KeyboardButton("🤝 Refer & Earn")],
            [KeyboardButton("🆘 Support"), KeyboardButton("⚖️ Terms")]
        ]
        await update.message.reply_text(
            "✅ Welcome to 24HoursOTP",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
        )

# ================= TEXT HANDLER =================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    # Recharge Mode Input
    if context.user_data.get("recharge_mode"):
        try:
            amount = float(text)
            if amount < db.MINIMUM_RECHARGE:
                await update.message.reply_text(f"Minimum recharge ₹{db.MINIMUM_RECHARGE}")
                return

            order = razorpay_create_order(amount)
            payment_link = f"https://rzp.io/l/{order['id']}"

            context.user_data["recharge_mode"] = False

            await update.message.reply_text(
                f"💳 Click below to pay ₹{amount}\n\n{payment_link}\n\nAfter payment, wallet will auto update."
            )
        except:
            await update.message.reply_text("Enter valid amount.")
        return

    if uid == ADMIN_USER_ID:
        await update.message.reply_text("Admin feature under development")
        return

    # USER PANEL
    if text == "🛒 Buy Number":
        services = db.get_services()
        if not services:
            await update.message.reply_text("⚠️ No services available.")
            return

        btns = [
            [InlineKeyboardButton(s["service_name"], callback_data=f"svc_{s['id']}")]
            for s in services
        ]

        await update.message.reply_text(
            "📱 Select Service",
            reply_markup=InlineKeyboardMarkup(btns)
        )

    elif text == "💰 Wallet":
        bal = db.get_user_balance(uid)
        kb = [[InlineKeyboardButton("Add Balance (Recharge)", callback_data="recharge_start")]]
        await update.message.reply_text(
            f"💰 Your Balance: ₹{bal:.2f}\n\nMinimum recharge: ₹{db.MINIMUM_RECHARGE}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown"
        )

    elif text == "📜 History":
        await update.message.reply_text("📜 History coming soon.")

    elif text == "🤝 Refer & Earn":
        bot_user = (await context.bot.get_me()).username
        await update.message.reply_text(
            f"🤝 Refer & Earn ₹10\n\nLink:\nt.me/{bot_user}?start=ref_{uid}\n\nFriend must recharge ₹30."
        )

    elif text == "🆘 Support":
        await update.message.reply_text("Send your message. Admin will reply.")

    elif text == "⚖️ Terms":
        await update.message.reply_text("⚖️ Terms: No refund after OTP delivered.")

# ================= CALLBACK =================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id

    if data == "recharge_start":
        context.user_data["recharge_mode"] = True
        await query.edit_message_text("💳 Enter amount to recharge (e.g., 100):")
        return

    if data.startswith("svc_"):
        sid = int(data.split("_")[1])
        context.user_data["service_id"] = sid

        servers = db.get_active_servers(sid)
        btns = []
        for s in servers:
            final_price = float(s["price"]) + 5
            btns.append([
                InlineKeyboardButton(
                    f"🟢 Server {s['server_number']} - ₹{final_price}",
                    callback_data=f"buy_{s['id']}_{final_price}"
                )
            ])

        await query.edit_message_text(
            "⚡ Select Server",
            reply_markup=InlineKeyboardMarkup(btns)
        )

    elif data.startswith("buy_"):
        _, srv_id, price = data.split("_")
        price = float(price)

        if not db.update_balance(uid, -price, "DEBIT", "Number Purchase"):
            await query.answer("Low balance!", show_alert=True)
            return

        service_id = context.user_data.get("service_id")
        service = db.get_service_by_id(service_id)

        res = get_number(service["provider_service_code"])

        if "ACCESS_NUMBER" in res:
            parts = res.split(":")
            act_id = parts[1]
            phone = parts[2]

            db.create_order(uid, service_id, int(srv_id), phone, act_id)

            await query.edit_message_text(
                f"📞 Number: `{phone}`\n⏳ Waiting for OTP...",
                parse_mode="Markdown"
            )

            asyncio.create_task(
                wait_for_otp(context, uid, act_id, price, service["service_name"])
            )

        else:
            db.update_balance(uid, price, "CREDIT", "Refund")
            await query.edit_message_text("❌ Failed. Refunded.")

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🚀 24HoursOTP Production Running...")
    app.run_polling()

if __name__ == "__main__":
    main()