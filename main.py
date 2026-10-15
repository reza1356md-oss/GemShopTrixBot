import os
import random
import logging

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

# بهتر است شماره کارت را در متغیر محیطی CARD_NUMBER در Railway تنظیم کنی.
CARD_NUMBER = os.getenv("CARD_NUMBER", "5022291575298169")
CARD_NAME = "رضا الله مددی آقبلاغی"

ADMIN_CHAT_ID = "b0KG4TR0BGyi09906a6a3aa2c8fc9c47"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GemShopTrixBot")

bot = Robot(token=BOT_TOKEN)

# سفارش فعال هر مشتری
pending_orders = {}

# سفارش‌ها بر اساس کد پیگیری
orders_by_tracking = {}

# کدهای استفاده‌شده
used_tracking_codes = set()

# سفارش‌هایی که مدیر باید برایشان دلیل رد ارسال کند
admin_reject_waiting = {}


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
    return str(getattr(message, "chat_id", ""))


def get_message_id(message):
    return getattr(message, "message_id", None)


def get_text(message):
    return (getattr(message, "text", "") or "").strip()


async def safe_send_message(chat_id, text, keypad=None):
    try:
        if keypad is not None:
            await bot.send_message(
                chat_id,
                text,
                chat_keypad=keypad,
                chat_keypad_type="New"
            )
        else:
            await bot.send_message(chat_id, text)

        return True

    except Exception:
        logger.exception("ارسال پیام ناموفق بود.")
        return False


async def safe_forward_message(from_chat_id, message_id, to_chat_id):
    if message_id is None:
        return False

    try:
        await bot.forward_message(
            from_chat_id,
            message_id,
            to_chat_id
        )
        return True

    except Exception:
        logger.exception("فوروارد پیام ناموفق بود.")
        return False


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
# منوی اصلی
# =========================================================

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


# =========================================================
# صفحه اول
# =========================================================

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
        .build()
    )


# =========================================================
# صفحه دوم
# =========================================================

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
        .build()
    )


# =========================================================
# دکمه تأیید سفارش اولیه
# =========================================================

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
            builder.button(
                id="cancel_order",
                text="❌ لغو"
            )
        )
        .build()
    )


# =========================================================
# دکمه تأیید اطلاعات
# =========================================================

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
            builder.button(
                id="cancel_order",
                text="❌ لغو سفارش"
            )
        )
        .build()
    )


# =========================================================
# دکمه‌های مدیر
# =========================================================

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
        builder
        .row(
            builder.button(
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
    "gem_110": {
        "name": "110 Gem",
        "price": "275✨",
        "type": "id"
    },
    "gem_231": {
        "name": "231 Gem",
        "price": "518✨",
        "type": "id"
    },
    "gem_583": {
        "name": "583 Gem",
        "price": "1375✨",
        "type": "id"
    },
    "gem_1060": {
        "name": "1060K Gem",
        "price": "2450✨",
        "type": "id"
    },
    "gem_2180": {
        "name": "2180K Gem",
        "price": "5,119✨",
        "type": "id"
    },
    "gem_5000": {
        "name": "5K Gem",
        "price": "12.3 MiL🌟",
        "type": "id"
    },
    "gem_11000": {
        "name": "11K GEM",
        "price": "23.890 MiL🌟",
        "type": "id"
    },
    "monthly_id": {
        "name": "Monthly",
        "price": "2.690💸",
        "type": "id"
    },
    "weekly_id": {
        "name": "Weekly",
        "price": "569💸",
        "type": "id"
    },
    "info_weekly": {
        "name": "هفتگی (450 جم)",
        "price": "399.000T💸",
        "type": "info"
    },
    "info_monthly": {
        "name": "ماهانه (2.600 جم)",
        "price": "1.950.000T💸",
        "type": "info"
    },
    "info_light": {
        "name": "هفتگی لایت (100 جم)",
        "price": "195.000T💸",
        "type": "info"
    },
    "offer_1": {
        "name": "آفر یک دلاری",
        "price": "220.000T💸",
        "type": "info"
    },
    "offer_2": {
        "name": "آفر دو دلاری",
        "price": "385.000T💸",
        "type": "info"
    },
    "levelup": {
        "name": "لول آپ پس (1250 Gem)",
        "price": "980",
        "type": "info"
    },
    "level_120": {
        "name": "120 جم",
        "price": "185",
        "type": "info"
    },
    "level_200": {
        "name": "200 جم",
        "price": "230",
        "type": "info"
    },
    "level_350": {
        "name": "350 جم",
        "price": "295",
        "type": "info"
    }
}


# =========================================================
# پیام درخواست اطلاعات
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
# ارسال اطلاعات پرداخت
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
        "پس از دریافت رسید، سفارش برای مدیر ارسال خواهد شد."
    )

    if not success:
        # اگر ارسال پرداخت ناموفق شد، امکان تلاش دوباره وجود داشته باشد.
        order["step"] = "collecting_info"
        order["status"] = "collecting_info"


# =========================================================
# پیام ثبت سفارش برای مشتری
# =========================================================

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
        "🙏 ممنون از اعتماد شما به TRIX SHOP ❤️"
    )


# =========================================================
# ارسال اطلاعات سفارش و رسید برای مدیر
# =========================================================

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
    )

    if order.get("gmail"):
        admin_text += (
            "📧 جی‌میل:\n"
            f"{order['gmail']}\n\n"
        )

    if order.get("account_name"):
        admin_text += (
            "👤 اسم اکانت:\n"
            f"{order['account_name']}\n\n"
        )

    if order.get("account_id"):
        admin_text += (
            "🆔 آیدی اکانت:\n"
            f"{order['account_id']}\n\n"
        )

    admin_text += (
        "🔐 رمز جیمیل:\n"
        "🔒\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📩 پیام‌ها و فایل‌های مرحله اطلاعات سفارش در ادامه می‌آیند.\n"
        "🧾 رسید پرداخت نیز در ادامه ارسال می‌شود.\n\n"
        "⏳ وضعیت: در انتظار بررسی رسید"
    )

    await safe_send_message(
        ADMIN_CHAT_ID,
        admin_text,
        admin_receipt_keypad(tracking_code)
    )

    # اطلاعات مرحله اول فقط پس از دریافت رسید برای مدیر فرستاده می‌شوند.
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

    # ارسال رسیدهای پرداخت
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
# شروع ربات
# =========================================================

@bot.on_message(commands=["start"])
async def start(bot: Robot, message: Message):
    await message.reply_keypad(
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
    await message.reply(
        "🆔 شناسه چت شما:\n\n"
        f"{message.chat_id}"
    )


# =========================================================
# مدیریت پیام‌های متنی و رسانه‌ای
# =========================================================

@bot.on_message()
async def normal_message(bot: Robot, message: Message):
    chat_id = get_chat_id(message)
    text = get_text(message)
    message_id = get_message_id(message)

    # مدیر: دریافت توضیح رد رسید
    if chat_id == ADMIN_CHAT_ID and chat_id in admin_reject_waiting:
        tracking_code = admin_reject_waiting.pop(chat_id)
        customer_chat_id, order = find_order_by_tracking(tracking_code)

        if not order:
            await message.reply("❌ سفارش موردنظر پیدا نشد.")
            return

        if not text:
            admin_reject_waiting[chat_id] = tracking_code
            await message.reply(
                "⚠️ لطفاً دلیل رد رسید را به صورت متن ارسال کنید."
            )
            return

        if order.get("status") != "waiting_confirmation":
            await message.reply(
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
            "━━━━━━━━━━━━━━\n\n"
            f"🎫 کد پیگیری:\n{tracking_code}\n\n"
            "📦 لطفاً توضیحات مدیر را بررسی کنید."
        )

        await message.reply(
            "❌ رسید رد شد و دلیل آن برای مشتری ارسال شد."
        )
        return

    # پیام‌های مدیر نباید به عنوان پیام مشتری پردازش شوند.
    if chat_id == ADMIN_CHAT_ID:
        return

    order = pending_orders.get(chat_id)

    if not order:
        return

    step = order.get("step")

    # -----------------------------------------------------
    # مرحله اطلاعات: فقط ذخیره می‌شود
    # -----------------------------------------------------

    if step == "collecting_info":
        order.setdefault("info_messages", []).append({
            "message_id": message_id,
            "chat_id": chat_id,
            "text": text
        })

        # متن‌ها ذخیره می‌شوند، ولی هر متن دلخواهی را
        # به صورت خودکار اسم یا آیدی حساب فرض نمی‌کنیم.
        if text:
            order.setdefault("info_texts", []).append(text)

        await message.reply_keypad(
            "✅ پیام شما برای سفارش ذخیره شد.\n\n"
            "اگر اطلاعات دیگری دارید، ارسال کنید.\n"
            "پس از تکمیل همه اطلاعات، دکمه تأیید را بزنید.",
            info_confirmation_keypad()
        )
        return

    # -----------------------------------------------------
    # مرحله دریافت رسید
    # -----------------------------------------------------

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
    try:
        button_id = message.aux_data.button_id
    except Exception:
        logger.exception("خواندن button_id ناموفق بود.")
        return

    if not button_id:
        return

    chat_id = get_chat_id(message)

    logger.info(
        "[CALLBACK] chat_id=%s button_id=%s",
        chat_id,
        button_id
    )

    # -----------------------------------------------------
    # دکمه‌های مدیریتی فقط برای مدیر
    # -----------------------------------------------------

    is_admin_button = (
        button_id.startswith("approve_receipt_")
        or button_id.startswith("reject_receipt_")
        or button_id.startswith("order_done_")
    )

    if is_admin_button and chat_id != ADMIN_CHAT_ID:
        await message.reply(
            "⛔ این دکمه فقط برای مدیر ربات قابل استفاده است."
        )
        return

    # -----------------------------------------------------
    # خرید
    # -----------------------------------------------------

    if button_id == "buy":
        await message.reply_keypad(
            "🛍 لیست جم با آیدی: 💎\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page1_keypad()
        )
        return

    if button_id == "next_page":
        await message.reply_keypad(
            "🛍 لیست جم با اطلاعات: 📌\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page2_keypad()
        )
        return

    if button_id == "back_page":
        await message.reply_keypad(
            "🛍 لیست جم با آیدی: 💎\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page1_keypad()
        )
        return

    # -----------------------------------------------------
    # لغو سفارش
    # -----------------------------------------------------

    if button_id == "cancel_order":
        if chat_id in pending_orders:
            old_order = pending_orders.pop(chat_id)
            old_tracking = old_order.get("tracking_code")

            if old_tracking:
                orders_by_tracking.pop(old_tracking, None)
                used_tracking_codes.discard(old_tracking)

        await message.reply_keypad(
            "❌ سفارش لغو شد.\n\n"
            "🛍 می‌توانید دوباره یک بسته انتخاب کنید:",
            main_menu()
        )
        return

    # -----------------------------------------------------
    # *** اصلاح اصلی ***
    # تأیید اطلاعات باید قبل از شرط confirm_ بررسی شود.
    # -----------------------------------------------------

    if button_id == "confirm_information":
        order = pending_orders.get(chat_id)

        if not order:
            await message.reply(
                "❌ سفارش فعالی پیدا نشد.\n"
                "لطفاً از منوی اصلی دوباره سفارش ثبت کنید."
            )
            return

        if order.get("step") != "collecting_info":
            await message.reply(
                "⚠️ مرحله اطلاعات این سفارش قبلاً تمام شده است."
            )
            return

        # ارسال اطلاعات پرداخت
        await send_payment_info(message, order)
        return

    # -----------------------------------------------------
    # انتخاب بسته
    # -----------------------------------------------------

    if button_id in PACKAGES:
        package = PACKAGES[button_id]

        await message.reply_keypad(
            "🛍 سفارش شما\n\n"
            "━━━━━━━━━━━━━━\n\n"
            "💎 بسته:\n"
            f"{package['name']}\n\n"
            "💰 قیمت:\n"
            f"{package['price']}\n\n"
            "━━━━━━━━━━━━━━\n\n"
            "آیا این بسته را تأیید می‌کنید?",
            order_keypad(button_id)
        )
        return

    # -----------------------------------------------------
    # تأیید اولیه سفارش
    # این شرط اکنون بعد از confirm_information قرار دارد.
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

        await message.reply_keypad(
            build_information_message(order),
            info_confirmation_keypad()
        )
        return

    # -----------------------------------------------------
    # تأیید رسید توسط مدیر
    # -----------------------------------------------------

    if button_id.startswith("approve_receipt_"):
        tracking_code = button_id.replace(
            "approve_receipt_", "", 1
        )

        customer_chat_id, order = find_order_by_tracking(
            tracking_code
        )

        if not order:
            await message.reply("❌ سفارش موردنظر پیدا نشد.")
            return

        if order.get("status") != "waiting_confirmation":
            await message.reply(
                "⚠️ این رسید قبلاً بررسی شده است."
            )
            return

        order["status"] = "in_progress"
        order["step"] = "in_progress"

        package = order["package"]

        await safe_send_message(
            customer_chat_id,
            "✅ رسید پرداخت شما تأیید شد.\n\n"
            "🔄 وضعیت سفارش شما:\n"
            "🟡در حال انجام سفارش\n\n"
            "━━━━━━━━━━━━━━━━━\n\n"
            f"🎫 کد پیگیری:\n{tracking_code}\n\n"
            "💎 لطفاً منتظر تکمیل سفارش باشید.\n\n"
            "🙏 ممنون از اعتماد شما به TRIX SHOP ❤️"
        )

        await safe_send_message(
            ADMIN_CHAT_ID,
            "✅ رسید سفارش تأیید شد.\n\n"
            f"💎 بسته:\n{package['name']}\n\n"
            f"💰 قیمت:\n{package['price']}\n\n"
            f"🎫 کد پیگیری:\n{tracking_code}\n\n"
            "پس از انجام سفارش، دکمه تکمیل را بزنید.",
            admin_done_keypad(tracking_code)
        )
        return

    # -----------------------------------------------------
    # رد رسید توسط مدیر
    # -----------------------------------------------------

    if button_id.startswith("reject_receipt_"):
        tracking_code = button_id.replace(
            "reject_receipt_", "", 1
        )

        customer_chat_id, order = find_order_by_tracking(
            tracking_code
        )

        if not order:
            await message.reply("❌ سفارش موردنظر پیدا نشد.")
            return

        if order.get("status") != "waiting_confirmation":
            await message.reply(
                "⚠️ این رسید قبلاً بررسی شده است."
            )
            return

        admin_reject_waiting[ADMIN_CHAT_ID] = tracking_code

        await message.reply(
            "❌ رد رسید انتخاب شد.\n\n"
            "📝 لطفاً دلیل رد رسید را در پیام بعدی به صورت متن ارسال کنید."
        )
        return

    # -----------------------------------------------------
    # تکمیل سفارش
    # -----------------------------------------------------

    if button_id.startswith("order_done_"):
        tracking_code = button_id.replace(
            "order_done_", "", 1
        )

        customer_chat_id, order = find_order_by_tracking(
            tracking_code
        )

        if not order:
            await message.reply("❌ سفارش موردنظر پیدا نشد.")
            return

        if order.get("status") != "in_progress":
            await message.reply(
                "⚠️ این سفارش هنوز در وضعیت انجام نیست."
            )
            return

        order["status"] = "completed"
        order["step"] = "completed"

        package = order["package"]

        await safe_send_message(
            customer_chat_id,
            "🎉 سفارش شما تکمیل شد ✅\n\n"
            f"💎 بسته:\n{package['name']}\n\n"
            f"💰 قیمت:\n{package['price']}\n\n"
            f"🎫 کد پیگیری:\n{tracking_code}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "✅ سفارش شما با موفقیت انجام شد.\n\n"
            "ممنونم بابت انتخابتون\n"
            "𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏 ❤️"
        )

        await message.reply(
            "🎉 سفارش تکمیل شد.\n\n"
            f"💎 بسته: {package['name']}\n"
            f"💰 قیمت: {package['price']}\n"
            f"🎫 کد پیگیری: {tracking_code}"
        )
        return

    # -----------------------------------------------------
    # پیگیری سفارش
    # -----------------------------------------------------

    if button_id == "orders":
        order = pending_orders.get(chat_id)

        if not order:
            await message.reply(
                "📦 در حال حاضر سفارش فعالی برای شما پیدا نشد."
            )
            return

        await message.reply(
            "📦 سفارش شما\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎫 کد پیگیری:\n{order['tracking_code']}\n\n"
            f"💎 محصول:\n{order['package']['name']}\n\n"
            f"💰 مبلغ:\n{order['package']['price']}\n\n"
            f"📌 وضعیت:\n{get_order_status_text(order)}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return

    # -----------------------------------------------------
    # پشتیبانی
    # -----------------------------------------------------

    if button_id == "support":
        await message.reply(
            "🆘 برای پشتیبانی با مدیر فروشگاه در ارتباط باشید.\n\n"
            f"📢 کانال: {SHOP_USERNAME}\n"
            f"🔗 {SHOP_LINK}"
        )
        return


# =========================================================
# اجرا
# =========================================================

logger.info("GemShopTrixBot is starting...")
bot.run()
