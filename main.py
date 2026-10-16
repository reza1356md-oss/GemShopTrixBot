import os
import random
import logging
import re
import inspect
import asyncio

from rubka import Robot, Message
from rubka.keypad import ChatKeypadBuilder


# =========================================================
# تنظیمات
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "متغیر BOT_TOKEN در تنظیمات محیطی ربات تعریف نشده است."
    )

SHOP_USERNAME = "@TRIX__SHOP"
SHOP_LINK = "https://rubika.ir/TRIX__SHOP"
GROUP_LINK = "https://rubika.ir/joing/JHGBHFGG0PKMOKLLUWKSWHNFELZKLBUJ"

CARD_NUMBER = os.getenv("CARD_NUMBER", "5022291575298169")
CARD_NAME = "رضا الله مددی آقبلاغی"

ADMIN_CHAT_ID = "b0KG4TR0BGyi09906a6a3aa2c8fc9c47"
SUPPORT_USERNAME = "@Me_HAJ_SAMiN"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("GemShopTrixBot")

bot = Robot(token=BOT_TOKEN)

pending_orders = {}
orders_by_tracking = {}
used_tracking_codes = set()
admin_reject_waiting = {}

chat_messages = {}

# مشتریانی که در حال نوشتن پیام پیگیری هستند
tracking_sessions = {}

# درخواست‌های پیگیری ارسال‌شده برای مدیر
tracking_requests = {}

# پاسخ مدیر که منتظر تأیید ارسال است
tracking_admin_drafts = {}

tracking_counter = 0


# =========================================================
# ابزارهای عمومی
# =========================================================

def generate_tracking_code():
    while True:
        code = f"#{random.randint(100000, 999999)}"

        if code not in used_tracking_codes:
            used_tracking_codes.add(code)
            return code


def find_order_by_tracking(tracking_code):
    data = orders_by_tracking.get(tracking_code)

    if not data:
        return None, None

    return data["customer_chat_id"], data["order"]


def get_chat_id(message):
    return str(getattr(message, "chat_id", "") or "")


def get_message_id(message):
    return getattr(message, "message_id", None)


def get_text(message):
    return (getattr(message, "text", "") or "").strip()


def remember_message(chat_id, message_id):
    if message_id is None:
        return

    chat_id = str(chat_id)
    chat_messages.setdefault(chat_id, [])

    if message_id not in chat_messages[chat_id]:
        chat_messages[chat_id].append(message_id)

    chat_messages[chat_id] = chat_messages[chat_id][-100:]


def extract_message_id(result):
    if result is None:
        return None

    message_id = getattr(result, "message_id", None)

    if message_id is not None:
        return message_id

    message_id = getattr(result, "id", None)

    if message_id is not None:
        return message_id

    if isinstance(result, dict):
        return result.get("message_id") or result.get("id")

    return None


async def resolve_result(result):
    if inspect.isawaitable(result):
        return await result

    return result


async def safe_send_message(chat_id, text, keypad=None):
    """
    ارسال پیام با ثبت خطا و شناسه پیام در صورت دسترسی.
    """
    chat_id = str(chat_id)

    try:
        if keypad is not None:
            result = await resolve_result(
                bot.send_message(
                    chat_id,
                    text,
                    chat_keypad=keypad,
                    chat_keypad_type="New"
                )
            )
        else:
            result = await resolve_result(
                bot.send_message(chat_id, text)
            )

        sent_message_id = extract_message_id(result)

        if sent_message_id is not None:
            remember_message(chat_id, sent_message_id)

        logger.info(
            "پیام ارسال شد | chat_id=%s | message_id=%s",
            chat_id,
            sent_message_id
        )
        return True

    except Exception:
        logger.exception(
            "ارسال پیام ناموفق بود | chat_id=%s",
            chat_id
        )
        return False


async def safe_reply(message, text, keypad=None):
    try:
        if keypad is not None:
            result = await resolve_result(
                message.reply_keypad(text, keypad)
            )
        else:
            result = await resolve_result(
                message.reply(text)
            )

        sent_message_id = extract_message_id(result)

        if sent_message_id is not None:
            remember_message(get_chat_id(message), sent_message_id)

        return True

    except Exception:
        logger.exception(
            "پاسخ به پیام ناموفق بود | chat_id=%s",
            get_chat_id(message)
        )
        return False


async def safe_forward_message(from_chat_id, message_id, to_chat_id):
    if message_id is None:
        return False

    try:
        await resolve_result(
            bot.forward_message(
                str(from_chat_id),
                message_id,
                str(to_chat_id)
            )
        )
        return True

    except Exception:
        logger.exception(
            "فوروارد پیام ناموفق بود | from=%s | to=%s | message_id=%s",
            from_chat_id,
            to_chat_id,
            message_id
        )
        return False


async def try_delete_message(chat_id, message_id):
    if message_id is None:
        return False

    for method_name in (
        "delete_message",
        "delete_messages",
        "delete_chat_message"
    ):
        method = getattr(bot, method_name, None)

        if not callable(method):
            continue

        try:
            await resolve_result(method(str(chat_id), message_id))
            return True
        except Exception:
            logger.debug(
                "حذف پیام با %s ناموفق بود.",
                method_name,
                exc_info=True
            )

    return False


async def clean_chat(chat_id):
    chat_id = str(chat_id)

    for message_id in reversed(chat_messages.get(chat_id, [])):
        await try_delete_message(chat_id, message_id)

    chat_messages[chat_id] = []


def get_order_status_text(order):
    statuses = {
        "collecting_info": "📝 در حال تکمیل اطلاعات",
        "collecting_receipt": "💳 در انتظار رسید پرداخت",
        "waiting_confirmation": "⏳ در انتظار تأیید رسید",
        "in_progress": "🔄 در حال انجام سفارش",
        "rejected": "❌ رسید رد شده",
        "completed": "✅ تکمیل شده",
        "cancelled": "❌ لغو شده",
    }

    return statuses.get(
        order.get("status", ""),
        "⏳ در حال بررسی"
    )


# =========================================================
# کیبوردها
# =========================================================

def home_button():
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id="back_home",
                text="🏠 بازگشت به صفحه اصلی"
            )
        )
        .build()
    )


def tracking_confirm_keypad():
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id="confirm_tracking_message",
                text="تأیید متن پیگیری 🌀"
            )
        )
        .row(
            builder.button(
                id="back_home",
                text="🏠 بازگشت به صفحه اصلی"
            )
        )
        .build()
    )


def admin_tracking_reply_keypad(request_id):
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id=f"send_tracking_reply_{request_id}",
                text="📨 ارسال پاسخ پیگیری سفارش"
            )
        )
        .build()
    )


def main_menu():
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(id="buy", text="💎 خرید جم"),
            builder.button(id="orders", text="📦 پیگیری سفارش")
        )
        .row(
            builder.button(id="support", text="🆘 پشتیبانی")
        )
        .build()
    )


def page1_keypad():
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(builder.button(id="gem_110", text="💎 110 Gem — 275✨"))
        .row(builder.button(id="gem_231", text="💎 231 Gem — 518✨"))
        .row(builder.button(id="gem_583", text="💎 583 Gem — 1375✨"))
        .row(builder.button(id="gem_1060", text="💎 1060K Gem — 2450✨"))
        .row(builder.button(id="gem_2180", text="💎 2180K Gem — 5,119✨"))
        .row(builder.button(id="gem_5000", text="💎 5K Gem — 12.3 MiL🌟"))
        .row(builder.button(id="gem_11000", text="💎 11K GEM — 23.890 MiL🌟"))
        .row(builder.button(id="monthly_id", text="📆 Monthly — 2.690💸"))
        .row(builder.button(id="weekly_id", text="🗓 Weekly — 549💸"))
        .row(builder.button(id="next_page", text="➡️ صفحه دوم"))
        .row(builder.button(id="back_home", text="🏠 بازگشت به صفحه اصلی"))
        .build()
    )


def page2_keypad():
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(builder.button(id="info_weekly", text="📌 هفتگی 450 جم — 399.000T💸"))
        .row(builder.button(id="info_monthly", text="📌 ماهانه 2.600 جم — 1.950.000T💸"))
        .row(builder.button(id="info_light", text="📌 هفتگی لایت 100 جم — 195.000T💸"))
        .row(builder.button(id="offer_1", text="🎁 آفر یک دلاری — 220.000T💸"))
        .row(builder.button(id="offer_2", text="🎁 آفر دو دلاری — 385.000T💸"))
        .row(builder.button(id="levelup", text="🏵 لول آپ پس 1250 Gem — 980"))
        .row(builder.button(id="level_120", text="⚠️ 120 جم — 185"))
        .row(builder.button(id="level_200", text="⚠️ 200 جم — 230"))
        .row(builder.button(id="level_350", text="⚠️ 350 جم — 295"))
        .row(builder.button(id="back_page", text="⬅️ صفحه اول"))
        .row(builder.button(id="back_home", text="🏠 بازگشت به صفحه اصلی"))
        .build()
    )


def order_keypad(package_id):
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id=f"confirm_{package_id}",
                text="✅ تأیید سفارش"
            )
        )
        .row(
            builder.button(id="cancel_order", text="❌ لغو")
        )
        .row(
            builder.button(
                id="back_home",
                text="🏠 بازگشت به صفحه اصلی"
            )
        )
        .build()
    )


def info_confirmation_keypad():
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id="confirm_information",
                text="تأیید اطلاعات و اطمینان صحت کامل ✅"
            )
        )
        .row(
            builder.button(id="cancel_order", text="❌ لغو سفارش")
        )
        .row(
            builder.button(
                id="back_home",
                text="🏠 بازگشت به صفحه اصلی"
            )
        )
        .build()
    )


def admin_receipt_keypad(tracking_code):
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id=f"approve_receipt_{tracking_code}",
                text="✅ تأیید رسید"
            ),
            builder.button(
                id=f"reject_receipt_{tracking_code}",
                text="❌ رد رسید"
            )
        )
        .build()
    )


def admin_done_keypad(tracking_code):
    builder = ChatKeypadBuilder()

    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(
                id=f"order_done_{tracking_code}",
                text="✅ تکمیل سفارش"
            )
        )
        .build()
    )


# =========================================================
# بسته‌ها
# =========================================================

PACKAGES = {
    "gem_110": {"name": "110 Gem", "price": "275✨", "type": "id"},
    "gem_231": {"name": "231 Gem", "price": "518✨", "type": "id"},
    "gem_583": {"name": "583 Gem", "price": "1375✨", "type": "id"},
    "gem_1060": {"name": "1060K Gem", "price": "2450✨", "type": "id"},
    "gem_2180": {"name": "2180K Gem", "price": "5,119✨", "type": "id"},
    "gem_5000": {"name": "5K Gem", "price": "12.3 MiL🌟", "type": "id"},
    "gem_11000": {"name": "11K GEM", "price": "23.890 MiL🌟", "type": "id"},
    "monthly_id": {"name": "Monthly", "price": "2.690💸", "type": "id"},
    "weekly_id": {"name": "Weekly", "price": "569💸", "type": "id"},
    "info_weekly": {"name": "هفتگی (450 جم)", "price": "399.000T💸", "type": "info"},
    "info_monthly": {"name": "ماهانه (2.600 جم)", "price": "1.950.000T💸", "type": "info"},
    "info_light": {"name": "هفتگی لایت (100 جم)", "price": "195.000T💸", "type": "info"},
    "offer_1": {"name": "آفر یک دلاری", "price": "220.000T💸", "type": "info"},
    "offer_2": {"name": "آفر دو دلاری", "price": "385.000T💸", "type": "info"},
    "levelup": {"name": "لول آپ پس (1250 Gem)", "price": "980", "type": "info"},
    "level_120": {"name": "120 جم", "price": "185", "type": "info"},
    "level_200": {"name": "200 جم", "price": "230", "type": "info"},
    "level_350": {"name": "350 جم", "price": "295", "type": "info"},
}


# =========================================================
# متن درخواست اطلاعات خرید
# =========================================================

def build_information_message(order):
    package = order["package"]

    if package["type"] == "id":
        return (
            "سفارش شما تأیید شد ✅\n\n"
            "💎 نوع سفارش:\n"
            f"{package['name']}\n\n"
            "💰 قیمت:\n"
            f"{package['price']}\n\n"
            "👤 اسم اکانت:\n"
            "[ ]\n\n"
            "🆔 آیدی اکانت:\n"
            "[ ]\n\n"
            "━━━━━━━━━━━━━━\n\n"
            "لطفاً اسم و آیدی اکانت خود را ارسال کنید.\n"
            "اگر اطلاعات تکمیلی یا تصویر لازم دارید، در همین مرحله ارسال کنید.\n\n"
            "وقتی همه اطلاعات را فرستادید، دکمه تأیید اطلاعات را بزنید."
        )

    return (
        "سفارش شما تأیید شد ✅\n\n"
        "💎 نوع سفارش:\n"
        f"{package['name']}\n\n"
        "💰 قیمت:\n"
        f"{package['price']}\n\n"
        "📧 جی‌میل:\n"
        "[ ]\n\n"
        "🔐 رمز جیمیل:\n"
        "[ ]\n\n"
        "📸 شات 10 تایی پشتیبانی:\n"
        "[ ]\n\n"
        "👤 اسم اکانت:\n"
        "[ ]\n\n"
        "🆔 آیدی اکانت:\n"
        "[ ]\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "اطلاعات غیرحساس و تصاویر لازم را در همین چت ارسال کنید.\n"
        "پس از ارسال همه موارد، دکمه تأیید اطلاعات را بزنید."
    )


# =========================================================
# اطلاعات پرداخت
# =========================================================

async def send_payment_info(message, order):
    order["step"] = "collecting_receipt"
    order["status"] = "collecting_receipt"

    package = order["package"]

    success = await safe_send_message(
        get_chat_id(message),
        "━━━━━━━━━━━━━━\n"
        "💳 اطلاعات پرداخت\n"
        "━━━━━━━━━━━━━━\n\n"
        "👤 نام صاحب کارت:\n"
        f"{CARD_NAME}\n\n"
        "💳 شماره کارت:\n"
        f"{CARD_NUMBER}\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "💎 محصول:\n"
        f"{package['name']}\n\n"
        "💰 مبلغ قابل پرداخت:\n"
        f"{package['price']}\n\n"
        "💸 لطفاً مبلغ دقیق سفارش را واریز کنید.\n\n"
        "🧾 پس از پرداخت، رسید را به صورت تصویر یا متن ارسال کنید.\n"
        "پس از دریافت رسید، سفارش برای مدیر ارسال خواهد شد.",
        home_button()
    )

    if not success:
        order["step"] = "collecting_info"
        order["status"] = "collecting_info"


async def send_receipt_received_message(customer_chat_id, order):
    tracking_code = order["tracking_code"]

    await safe_send_message(
        customer_chat_id,
        "🧾 رسید پرداخت شما دریافت شد ✅\n\n"
        "📦 سفارش شما با موفقیت ثبت شد.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "⏳ وضعیت سفارش شما:\n"
        "در انتظار تأیید رسید\n\n"
        f"🎫 کد پیگیری سفارش:\n{tracking_code}\n\n"
        "💎 لطفاً این کد پیگیری را نزد خود نگه دارید.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "🙏 ممنون از اعتماد شما به TRIX SHOP ❤️",
        home_button()
    )


async def notify_admin(order, customer_chat_id):
    package = order["package"]
    tracking_code = order["tracking_code"]

    admin_text = (
        "🔔 سفارش جدید برای بررسی\n\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🎫 کد پیگیری:\n{tracking_code}\n\n"
        f"💎 محصول:\n{package['name']}\n\n"
        f"💰 مبلغ:\n{package['price']}\n\n"
        f"🆔 شناسه چت مشتری:\n{customer_chat_id}\n\n"
        "🔐 رمز جیمیل:\n"
        "دریافت یا ارسال نمی‌شود 🔒\n\n"
        "📩 پیام‌ها و فایل‌های مرحله اطلاعات سفارش در ادامه می‌آیند.\n"
        "🧾 رسید پرداخت نیز در ادامه ارسال می‌شود.\n\n"
        "⏳ وضعیت: در انتظار بررسی رسید"
    )

    await safe_send_message(
        ADMIN_CHAT_ID,
        admin_text,
        admin_receipt_keypad(tracking_code)
    )

    for item in order.get("info_messages", []):
        forwarded = await safe_forward_message(
            item["chat_id"],
            item["message_id"],
            ADMIN_CHAT_ID
        )

        if not forwarded and item.get("text"):
            await safe_send_message(
                ADMIN_CHAT_ID,
                "📝 پیام ثبت‌شده مشتری:\n" + item["text"]
            )

    for item in order.get("receipt_messages", []):
        forwarded = await safe_forward_message(
            item["chat_id"],
            item["message_id"],
            ADMIN_CHAT_ID
        )

        if not forwarded and item.get("text"):
            await safe_send_message(
                ADMIN_CHAT_ID,
                "🧾 متن رسید مشتری:\n" + item["text"]
            )


# =========================================================
# پیگیری سفارش: ارسال پیام‌های مشتری برای مدیر
# =========================================================

async def send_tracking_request_to_admin(request_id):
    request_data = tracking_requests.get(request_id)

    if not request_data:
        logger.error("درخواست پیگیری پیدا نشد: %s", request_id)
        return False

    customer_chat_id = request_data["customer_chat_id"]

    admin_text = (
        "📩 درخواست جدید پیگیری سفارش\n\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🆔 شناسه چت مشتری:\n{customer_chat_id}\n\n"
        f"🎫 کد پیگیری مشتری:\n"
        f"{request_data.get('tracking_code') or 'ارسال نشده'}\n\n"
        f"🆔 شماره درخواست:\n{request_id}\n\n"
        "📥 پیام‌های مشتری در ادامه ارسال می‌شوند.\n\n"
        "✍️ برای پاسخ، دکمه زیر را بزنید؛ سپس پاسخ خود را به صورت متن ارسال کنید."
    )

    # ابتدا پیام اصلی درخواست به مدیر ارسال می‌شود
    admin_sent = await safe_send_message(ADMIN_CHAT_ID, admin_text)

    if not admin_sent:
        logger.error(
            "ارسال خلاصه پیگیری به مدیر ناموفق بود؛ request_id=%s",
            request_id
        )
        return False

    # سپس پیام‌های مشتری یکی‌یکی فوروارد می‌شوند
    for item in request_data.get("messages", []):
        message_id = item.get("message_id")

        if message_id is not None:
            forwarded = await safe_forward_message(
                customer_chat_id,
                message_id,
                ADMIN_CHAT_ID
            )

            if forwarded:
                continue

        # اگر پیام قابل فوروارد نبود، حداقل متن آن را برای مدیر بفرست
        if item.get("text"):
            await safe_send_message(
                ADMIN_CHAT_ID,
                "📝 متن پیام مشتری:\n" + item["text"]
            )
        else:
            await safe_send_message(
                ADMIN_CHAT_ID,
                "⚠️ یکی از پیام‌های مشتری قابل فوروارد نبود.\n"
                f"شناسه چت مشتری: {customer_chat_id}\n"
                f"شناسه پیام: {message_id}"
            )

    await safe_send_message(
        ADMIN_CHAT_ID,
        "برای پاسخ به این درخواست، دکمه زیر را بزنید.\n"
        f"شماره درخواست: {request_id}",
        admin_tracking_reply_keypad(request_id)
    )

    request_data["sent_to_admin"] = True
    logger.info("درخواست پیگیری برای مدیر ارسال شد: %s", request_id)
    return True


# =========================================================
# شروع
# =========================================================

@bot.on_message(commands=["start"])
async def start(bot: Robot, message: Message):
    chat_id = get_chat_id(message)
    remember_message(chat_id, get_message_id(message))

    tracking_sessions.pop(chat_id, None)

    await safe_reply(
        message,
        "🤖 ربات خرید جم تریکس شاپ خوش آمدید 🫠\n\n"
        "📢 چنل اصلی آگهی اکانت: 👇\n"
        "@TRIX__SHOP\n\n"
        "💬 گپ اصلی شاپ: 👇\n"
        f"{GROUP_LINK}\n\n"
        "از منوی زیر انتخاب کنید:",
        main_menu()
    )


# =========================================================
# شناسه کاربر
# =========================================================

@bot.on_message(commands=["myid"])
async def my_id(bot: Robot, message: Message):
    await safe_reply(
        message,
        "🆔 شناسه چت شما:\n\n"
        f"{message.chat_id}"
    )


# =========================================================
# دریافت پیام‌های مشتری و مدیر
# =========================================================

@bot.on_message()
async def normal_message(bot: Robot, message: Message):
    chat_id = get_chat_id(message)
    text = get_text(message)
    message_id = get_message_id(message)

    remember_message(chat_id, message_id)

    # -----------------------------------------------------
    # پیام‌های مدیر
    # -----------------------------------------------------

    if chat_id == ADMIN_CHAT_ID:
        # دریافت دلیل رد رسید
        if chat_id in admin_reject_waiting:
            tracking_code = admin_reject_waiting.pop(chat_id)
            customer_chat_id, order = find_order_by_tracking(
                tracking_code
            )

            if not order:
                await safe_reply(message, "❌ سفارش موردنظر پیدا نشد.")
                return

            if not text:
                admin_reject_waiting[chat_id] = tracking_code
                await safe_reply(
                    message,
                    "⚠️ لطفاً دلیل رد رسید را به صورت متن ارسال کنید."
                )
                return

            if order.get("status") != "waiting_confirmation":
                await safe_reply(
                    message,
                    "⚠️ این سفارش دیگر در انتظار بررسی رسید نیست."
                )
                return

            order["status"] = "rejected"
            order["step"] = "rejected"
            order["reject_reason"] = text

            await safe_send_message(
                customer_chat_id,
                "❌ رسید پرداخت شما رد شد.\n\n"
                "📌 توضیح مدیر:\n"
                f"{text}\n\n"
                f"🎫 کد پیگیری:\n{tracking_code}",
                home_button()
            )

            await safe_reply(
                message,
                "❌ رسید رد شد و دلیل آن برای مشتری ارسال شد."
            )
            return

        # مدیر در حال نوشتن پاسخ پیگیری است
        if chat_id in tracking_admin_drafts:
            draft = tracking_admin_drafts[chat_id]

            if not text:
                await safe_reply(
                    message,
                    "⚠️ لطفاً پاسخ پیگیری را به صورت متن ارسال کنید."
                )
                return

            draft["reply_text"] = text
            draft["reply_message_id"] = message_id

            await safe_reply(
                message,
                "✅ پاسخ شما ثبت شد.\n\n"
                "اکنون دکمه «ارسال پاسخ پیگیری سفارش» را بزنید.",
                admin_tracking_reply_keypad(draft["request_id"])
            )
            return

        return

    # -----------------------------------------------------
    # پیام‌های مشتری در حالت پیگیری
    # -----------------------------------------------------

    session = tracking_sessions.get(chat_id)

    if session is not None:
        session.setdefault("messages", []).append({
            "message_id": message_id,
            "text": text,
        })

        if text:
            session.setdefault("texts", []).append(text)

        # مهم: در این مرحله عمداً هیچ پاسخی برای مشتری ارسال نمی‌شود.
        logger.info(
            "پیام پیگیری ذخیره شد | chat_id=%s | message_id=%s",
            chat_id,
            message_id
        )
        return

    # -----------------------------------------------------
    # پیام‌های مربوط به سفارش خرید
    # -----------------------------------------------------

    order = pending_orders.get(chat_id)

    if not order:
        return

    step = order.get("step")

    if step == "collecting_info":
        order.setdefault("info_messages", []).append({
            "message_id": message_id,
            "chat_id": chat_id,
            "text": text
        })

        if text:
            order.setdefault("info_texts", []).append(text)

        await safe_reply(
            message,
            "✅ پیام شما برای سفارش ذخیره شد.\n\n"
            "اگر اطلاعات دیگری دارید، ارسال کنید.\n"
            "پس از تکمیل همه اطلاعات، دکمه تأیید را بزنید.",
            info_confirmation_keypad()
        )
        return

    if step == "collecting_receipt":
        order.setdefault("receipt_messages", []).append({
            "message_id": message_id,
            "chat_id": chat_id,
            "text": text
        })

        order["status"] = "waiting_confirmation"
        order["step"] = "waiting_confirmation"

        if not order.get("admin_notified"):
            order["admin_notified"] = True
            await notify_admin(order, chat_id)

        await send_receipt_received_message(chat_id, order)
        return


# =========================================================
# دکمه‌ها
# =========================================================

@bot.on_callback()
async def all_callbacks(bot: Robot, message: Message):
    global tracking_counter

    try:
        button_id = message.aux_data.button_id
    except Exception:
        logger.exception("خواندن button_id ناموفق بود.")
        return

    if not button_id:
        return

    chat_id = get_chat_id(message)
    remember_message(chat_id, get_message_id(message))

    logger.info(
        "[CALLBACK] chat_id=%s button_id=%s",
        chat_id,
        button_id
    )

    # -----------------------------------------------------
    # محدودیت دکمه‌های مدیریتی
    # -----------------------------------------------------

    is_admin_button = (
        button_id.startswith("approve_receipt_")
        or button_id.startswith("reject_receipt_")
        or button_id.startswith("order_done_")
        or button_id.startswith("send_tracking_reply_")
    )

    if is_admin_button and chat_id != ADMIN_CHAT_ID:
        await safe_reply(
            message,
            "⛔ این دکمه فقط برای مدیر ربات قابل استفاده است."
        )
        return

    # -----------------------------------------------------
    # پاسخ پیگیری مدیر
    # -----------------------------------------------------

    if button_id.startswith("send_tracking_reply_"):
        request_id = button_id.replace(
            "send_tracking_reply_", "", 1
        )

        request_data = tracking_requests.get(request_id)

        if not request_data:
            await safe_reply(
                message,
                "❌ درخواست پیگیری پیدا نشد یا قبلاً پاسخ داده شده است."
            )
            return

        draft = tracking_admin_drafts.get(ADMIN_CHAT_ID)

        # اگر پاسخ آماده است، آن را ارسال کن
        if draft and draft.get("request_id") == request_id:
            reply_text = (draft.get("reply_text") or "").strip()

            if not reply_text:
                await safe_reply(
                    message,
                    "⚠️ هنوز پاسخ خود را ننوشته‌اید.\n"
                    "ابتدا پاسخ را به صورت پیام متنی ارسال کنید."
                )
                return

            customer_chat_id = request_data["customer_chat_id"]

            sent = await safe_send_message(
                customer_chat_id,
                "📩 پاسخ پیگیری سفارش شما:\n\n"
                f"{reply_text}\n\n"
                "━━━━━━━━━━━━━━\n\n"
                "🔸 𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏 | تریکس شاپ 🔸",
                home_button()
            )

            if sent:
                tracking_requests.pop(request_id, None)
                tracking_admin_drafts.pop(ADMIN_CHAT_ID, None)

                await safe_reply(
                    message,
                    "✅ پاسخ پیگیری با موفقیت برای مشتری ارسال شد."
                )
            else:
                await safe_reply(
                    message,
                    "❌ ارسال پاسخ ناموفق بود. خطای ارسال در لاگ ثبت شده است."
                )

            return

        # پاسخ هنوز نوشته نشده است
        tracking_admin_drafts[ADMIN_CHAT_ID] = {
            "request_id": request_id,
            "reply_text": "",
            "reply_message_id": None,
        }

        await safe_reply(
            message,
            "✍️ اکنون پاسخ خود را به صورت یک پیام متنی ارسال کنید.\n\n"
            "بعد از ارسال پاسخ، دکمه «ارسال پاسخ پیگیری سفارش» را بزنید."
        )
        return

    # -----------------------------------------------------
    # تأیید رسید توسط مدیر
    # -----------------------------------------------------

    if button_id.startswith("approve_receipt_"):
        tracking_code = button_id.replace("approve_receipt_", "", 1)
        customer_chat_id, order = find_order_by_tracking(tracking_code)

        if not order:
            await safe_reply(message, "❌ سفارش پیدا نشد.")
            return

        if order.get("status") != "waiting_confirmation":
            await safe_reply(message, "⚠️ این رسید قبلاً بررسی شده است.")
            return

        order["status"] = "in_progress"
        order["step"] = "in_progress"

        package = order["package"]

        await safe_send_message(
            customer_chat_id,
            "✅ رسید پرداخت شما تأیید شد.\n\n"
            "🔄 وضعیت سفارش شما: در حال انجام سفارش\n\n"
            f"🎫 کد پیگیری:\n{tracking_code}\n\n"
            "🙏 ممنون از اعتماد شما به TRIX SHOP ❤️",
            home_button()
        )

        await safe_send_message(
            ADMIN_CHAT_ID,
            "✅ رسید سفارش تأیید شد.\n\n"
            f"💎 بسته: {package['name']}\n"
            f"💰 قیمت: {package['price']}\n"
            f"🎫 کد پیگیری: {tracking_code}\n\n"
            "پس از انجام سفارش، دکمه تکمیل را بزنید.",
            admin_done_keypad(tracking_code)
        )
        return

    # -----------------------------------------------------
    # رد رسید توسط مدیر
    # -----------------------------------------------------

    if button_id.startswith("reject_receipt_"):
        tracking_code = button_id.replace("reject_receipt_", "", 1)
        customer_chat_id, order = find_order_by_tracking(tracking_code)

        if not order:
            await safe_reply(message, "❌ سفارش پیدا نشد.")
            return

        if order.get("status") != "waiting_confirmation":
            await safe_reply(message, "⚠️ این رسید قبلاً بررسی شده است.")
            return

        admin_reject_waiting[ADMIN_CHAT_ID] = tracking_code

        await safe_reply(
            message,
            "❌ رد رسید انتخاب شد.\n\n"
            "📝 لطفاً دلیل رد رسید را به صورت متن ارسال کنید."
        )
        return

    # -----------------------------------------------------
    # تکمیل سفارش توسط مدیر
    # -----------------------------------------------------

    if button_id.startswith("order_done_"):
        tracking_code = button_id.replace("order_done_", "", 1)
        customer_chat_id, order = find_order_by_tracking(tracking_code)

        if not order:
            await safe_reply(message, "❌ سفارش پیدا نشد.")
            return

        if order.get("status") != "in_progress":
            await safe_reply(message, "⚠️ این سفارش در وضعیت انجام نیست.")
            return

        order["status"] = "completed"
        order["step"] = "completed"

        package = order["package"]

        await safe_send_message(
            customer_chat_id,
            "🎉 سفارش شما تکمیل شد ✅\n\n"
            f"💎 بسته: {package['name']}\n"
            f"💰 قیمت: {package['price']}\n"
            f"🎫 کد پیگیری: {tracking_code}\n\n"
            "ممنونم بابت انتخابتون\n"
            "𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏 ❤️",
            home_button()
        )

        await safe_reply(
            message,
            "🎉 سفارش تکمیل شد.\n"
            f"💎 بسته: {package['name']}\n"
            f"🎫 کد پیگیری: {tracking_code}"
        )
        return

    # -----------------------------------------------------
    # بازگشت به صفحه اصلی
    # -----------------------------------------------------

    if button_id == "back_home":
        tracking_sessions.pop(chat_id, None)

        await clean_chat(chat_id)

        await safe_reply(
            message,
            "🏠 به صفحه اصلی برگشتید.\n\n"
            "یکی از گزینه‌های زیر را انتخاب کنید:",
            main_menu()
        )
        return

    # -----------------------------------------------------
    # خرید جم
    # -----------------------------------------------------

    if button_id == "buy":
        await safe_reply(
            message,
            "🛍 لیست جم با آیدی: 💎\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page1_keypad()
        )
        return

    if button_id == "next_page":
        await safe_reply(
            message,
            "🛍 لیست جم با اطلاعات: 📌\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page2_keypad()
        )
        return

    if button_id == "back_page":
        await safe_reply(
            message,
            "🛍 لیست جم با آیدی: 💎\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page1_keypad()
        )
        return

    if button_id == "cancel_order":
        if chat_id in pending_orders:
            old_order = pending_orders.pop(chat_id)
            old_tracking = old_order.get("tracking_code")

            if old_tracking:
                orders_by_tracking.pop(old_tracking, None)
                used_tracking_codes.discard(old_tracking)

        await safe_reply(
            message,
            "❌ سفارش لغو شد.\n\n"
            "🛍 می‌توانید دوباره یک بسته انتخاب کنید:",
            main_menu()
        )
        return

    # -----------------------------------------------------
    # تأیید اطلاعات سفارش خرید
    # -----------------------------------------------------

    if button_id == "confirm_information":
        order = pending_orders.get(chat_id)

        if not order:
            await safe_reply(
                message,
                "❌ سفارش فعالی پیدا نشد.",
                home_button()
            )
            return

        if order.get("step") != "collecting_info":
            await safe_reply(
                message,
                "⚠️ مرحله اطلاعات این سفارش قبلاً تمام شده است.",
                home_button()
            )
            return

        await send_payment_info(message, order)
        return

    # -----------------------------------------------------
    # انتخاب بسته
    # -----------------------------------------------------

    if button_id in PACKAGES:
        package = PACKAGES[button_id]

        await safe_reply(
            message,
            "🛍 سفارش شما\n\n"
            "━━━━━━━━━━━━━━\n\n"
            f"💎 بسته:\n{package['name']}\n\n"
            f"💰 قیمت:\n{package['price']}\n\n"
            "━━━━━━━━━━━━━━\n\n"
            "آیا این بسته را تأیید می‌کنید؟",
            order_keypad(button_id)
        )
        return

    # -----------------------------------------------------
    # تأیید اولیه سفارش
    # -----------------------------------------------------

    if button_id.startswith("confirm_"):
        package_id = button_id.replace("confirm_", "", 1)

        if package_id not in PACKAGES:
            return

        package = PACKAGES[package_id]
        tracking_code = generate_tracking_code()

        old_order = pending_orders.get(chat_id)

        if old_order:
            old_tracking = old_order.get("tracking_code")
            if old_tracking:
                orders_by_tracking.pop(old_tracking, None)

        order = {
            "package": package,
            "package_id": package_id,
            "tracking_code": tracking_code,
            "step": "collecting_info",
            "status": "collecting_info",
            "info_messages": [],
            "info_texts": [],
            "receipt_messages": [],
            "admin_notified": False
        }

        pending_orders[chat_id] = order

        orders_by_tracking[tracking_code] = {
            "customer_chat_id": chat_id,
            "order": order
        }

        await safe_reply(
            message,
            build_information_message(order),
            info_confirmation_keypad()
        )
        return

    # -----------------------------------------------------
    # پیگیری سفارش: شروع
    # -----------------------------------------------------

    if button_id == "orders":
        tracking_sessions[chat_id] = {
            "messages": [],
            "texts": [],
        }

        await safe_reply(
            message,
            "از اینکه ♻️**تریکس شاپ** | 𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏♻️ "
            "را انتخاب کرده‌اید متشکریم.🔆\n"
            "ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ\n\n"
            "متن و مشکل مورد نظرتون رو همراه کد پیگیری سفارشتون ارسال کنید "
            "و گزینه تأیید متن پیگیری 🌀 را کلیک کنید 🥰",
            tracking_confirm_keypad()
        )
        return

    # -----------------------------------------------------
    # پیگیری سفارش: تأیید پیام
    # -----------------------------------------------------

    if button_id == "confirm_tracking_message":
        session = tracking_sessions.get(chat_id)

        logger.info(
            "تأیید پیگیری | chat_id=%s | session_exists=%s",
            chat_id,
            session is not None
        )

        if session is None:
            await safe_reply(
                message,
                "⚠️ درخواست پیگیری فعالی پیدا نشد.\n"
                "لطفاً دوباره از صفحه اصلی گزینه «پیگیری سفارش» را انتخاب کنید.",
                home_button()
            )
            return

        if not session.get("messages"):
            await safe_reply(
                message,
                "⚠️ هنوز پیامی ارسال نکرده‌اید.\n"
                "ابتدا متن، عکس، ویس یا پیام موردنظر را ارسال کنید.",
                tracking_confirm_keypad()
            )
            return

        tracking_counter += 1
        request_id = str(tracking_counter)

        all_text = "\n".join(session.get("texts", []))
        match = re.search(r"#[0-9]{4,}", all_text)
        tracking_code = match.group(0) if match else None

        tracking_requests[request_id] = {
            "customer_chat_id": chat_id,
            "messages": list(session["messages"]),
            "tracking_code": tracking_code,
            "sent_to_admin": False,
        }

        # پایان حالت جمع‌آوری پیام
        tracking_sessions.pop(chat_id, None)

        # اول پاسخ قطعی به مشتری
        customer_notified = await safe_send_message(
            chat_id,
            "پیام شما دریافت شد✅\n"
            "در اولین فرصت به پیام شما پاسخ داده خواهد شد🫠\n"
            "𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏 | تریکس شاپ",
            home_button()
        )

        # سپس ارسال درخواست برای مدیر
        admin_notified = await send_tracking_request_to_admin(request_id)

        if not admin_notified:
            logger.error(
                "ارسال درخواست پیگیری به مدیر ناموفق بود. request_id=%s",
                request_id
            )

            await safe_send_message(
                chat_id,
                "⚠️ پیام شما ثبت شده، اما ارسال خودکار آن برای مدیریت با مشکل روبه‌رو شد.\n"
                "لطفاً کمی بعد دوباره از گزینه پیگیری سفارش استفاده کنید.",
                home_button()
            )

        if not customer_notified:
            logger.error(
                "ارسال پیام تأیید به مشتری ناموفق بود. chat_id=%s",
                chat_id
            )

        return

    # -----------------------------------------------------
    # پشتیبانی
    # -----------------------------------------------------

    if button_id == "support":
        await safe_reply(
            message,
            "ایدی مدیریت بات👇\n"
            "@Me_HAJ_SAMiN\n\n"
            "پیام خود را برای مدیریت ارسال کرده\n"
            "و در اولین فرصت به پیغام شما پاسخ\n"
            "داده خواهد شد🌹\n\n"
            "🔸𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏 | تریکس شاپ🔸",
            home_button()
        )
        return


# =========================================================
# اجرا
# =========================================================

logger.info("GemShopTrixBot is starting...")
bot.run()
