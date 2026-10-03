import os
import random

from rubka import Robot, Message
from rubka.keypad import ChatKeypadBuilder


BOT_TOKEN = os.getenv("BOT_TOKEN")

SHOP_USERNAME = "@TRIX__SHOP"
SHOP_LINK = "https://rubika.ir/TRIX__SHOP"
GROUP_LINK = "https://rubika.ir/joing/JHGBHFGG0PKMOKLLUWKSWHNFELZKLBUJ"

# شماره کارت خودت را اینجا قرار بده
CARD_NUMBER = "5022291575298169"
CARD_NAME = "رضا الله مددی آقبلاغی"

ADMIN_CHAT_ID = "b0KG4TR0BGyi09906a6a3aa2c8fc9c47"

bot = Robot(token=BOT_TOKEN)

# سفارش فعال هر مشتری
pending_orders = {}

# نگهداری مستقیم سفارش‌ها بر اساس کد پیگیری
orders_by_tracking = {}

# کدهای پیگیری استفاده‌شده
used_tracking_codes = set()

# مدیر در انتظار توضیح رد کدام سفارش است
admin_reject_waiting = {}


# =========================================================
# ساخت کد پیگیری 6 رقمی
# =========================================================

def generate_tracking_code():
    while True:
        code = f"#{random.randint(100000, 999999)}"

        if code not in used_tracking_codes:
            used_tracking_codes.add(code)
            return code


# =========================================================
# پیدا کردن سفارش با کد پیگیری
# =========================================================

def find_order_by_tracking(tracking_code):
    data = orders_by_tracking.get(tracking_code)

    if not data:
        return None, None

    return data["customer_chat_id"], data["order"]


# =========================================================
# منوی اصلی
# =========================================================

def main_menu():
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id="buy",
                text="💎 خرید جم"
            ),
            builder.button(
                id="orders",
                text="📦 پیگیری سفارش"
            )
        )
        .row(
            builder.button(
                id="support",
                text="🆘 پشتیبانی"
            )
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
        .row(
            builder.button(
                id="gem_110",
                text="💎 110 Gem — 275✨"
            )
        )
        .row(
            builder.button(
                id="gem_231",
                text="💎 231 Gem — 518✨"
            )
        )
        .row(
            builder.button(
                id="gem_583",
                text="💎 583 Gem — 1375✨"
            )
        )
        .row(
            builder.button(
                id="gem_1060",
                text="💎 1060K Gem — 2450✨"
            )
        )
        .row(
            builder.button(
                id="gem_2180",
                text="💎 2180K Gem — 5,119✨"
            )
        )
        .row(
            builder.button(
                id="gem_5000",
                text="💎 5K Gem — 12.3 MiL🌟"
            )
        )
        .row(
            builder.button(
                id="gem_11000",
                text="💎 11K GEM — 23.890 MiL🌟"
            )
        )
        .row(
            builder.button(
                id="monthly_id",
                text="📆 Monthly — 2.690💸"
            )
        )
        .row(
            builder.button(
                id="weekly_id",
                text="🗓 Weekly — 549💸"
            )
        )
        .row(
            builder.button(
                id="next_page",
                text="➡️ صفحه دوم"
            )
        )
        .build()
    )


# =========================================================
# صفحه دوم
# =========================================================

def page2_keypad():
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id="info_weekly",
                text="📌 هفتگی 450 جم — 399.000T💸"
            )
        )
        .row(
            builder.button(
                id="info_monthly",
                text="📌 ماهانه 2.600 جم — 1.950.000T💸"
            )
        )
        .row(
            builder.button(
                id="info_light",
                text="📌 هفتگی لایت 100 جم — 195.000T💸"
            )
        )
        .row(
            builder.button(
                id="offer_1",
                text="🎁 آفر یک دلاری — 220.000T💸"
            )
        )
        .row(
            builder.button(
                id="offer_2",
                text="🎁 آفر دو دلاری — 385.000T💸"
            )
        )
        .row(
            builder.button(
                id="levelup",
                text="🏵 لول آپ پس 1250 Gem — 980"
            )
        )
        .row(
            builder.button(
                id="level_120",
                text="⚠️ 120 جم — 185"
            )
        )
        .row(
            builder.button(
                id="level_200",
                text="⚠️ 200 جم — 230"
            )
        )
        .row(
            builder.button(
                id="level_350",
                text="⚠️ 350 جم — 295"
            )
        )
        .row(
            builder.button(
                id="back_page",
                text="⬅️ صفحه اول"
            )
        )
        .build()
    )


# =========================================================
# دکمه تأیید و لغو سفارش
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
# دکمه‌های مدیر برای بررسی رسید
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


# =========================================================
# دکمه تکمیل سفارش برای مدیر
# =========================================================

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
# شروع
# =========================================================

@bot.on_message(commands=["start"])
async def start(bot: Robot, message: Message):

    await message.reply_keypad(
        "🤖 ربات خرید جم تریکس شاپ خوش آمدید 🫠\n\n"
        "📢 چنل اصلی اگهی اکانت : 👇\n"
        "@TRIX__SHOP\n\n"
        "💬 گپ اصلی شاپ : 👇\n"
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
# پیام‌های متنی
# =========================================================

@bot.on_message()
async def normal_message(bot: Robot, message: Message):

    text = (message.text or "").strip()
    chat_id = message.chat_id

    # =====================================================
    # مدیر: دریافت توضیح رد رسید
    # =====================================================

    if chat_id == ADMIN_CHAT_ID:

        if chat_id in admin_reject_waiting:

            tracking_code = admin_reject_waiting.pop(
                chat_id
            )

            customer_chat_id, order = find_order_by_tracking(
                tracking_code
            )

            if not order:

                await message.reply(
                    "❌ سفارش موردنظر پیدا نشد.\n"
                    "ممکن است سفارش مربوط به اجرای قبلی ربات باشد."
                )

                return

            if not text:

                admin_reject_waiting[chat_id] = tracking_code

                await message.reply(
                    "⚠️ لطفاً توضیح رد رسید را به صورت متن ارسال کنید."
                )

                return

            order["status"] = "rejected"
            order["step"] = "rejected"
            order["reject_reason"] = text

            try:

                await bot.send_message(
                    customer_chat_id,

                    "❌ رسید پرداخت شما رد شد.\n\n"

                    "📌 توضیح مدیر:\n"
                    f"{text}\n\n"

                    "━━━━━━━━━━━━━━\n\n"

                    f"🎫 کد پیگیری:\n"
                    f"{tracking_code}\n\n"

                    "📦 لطفاً توضیحات مدیر را بررسی کنید."
                )

            except Exception as e:

                print(
                    "خطا در ارسال دلیل رد به مشتری:",
                    e
                )

            await message.reply(
                "❌ رسید سفارش رد شد.\n\n"
                "📨 توضیحات رد برای مشتری ارسال شد."
            )

            return

    # =====================================================
    # اگر سفارش فعال نیست
    # =====================================================

    if chat_id not in pending_orders:
        return

    order = pending_orders[chat_id]
    step = order["step"]

    # =====================================================
    # رسید پرداخت
    # =====================================================

    if step == "receipt":

        file_data = getattr(
            message,
            "file",
            None
        )

        # رسید تصویری / فایل
        if file_data:

            order["receipt"] = file_data
            order["receipt_message_id"] = message.message_id
            order["step"] = "waiting_confirmation"
            order["status"] = "waiting_confirmation"

            await notify_admin(
                bot,
                message,
                order
            )

            try:

                await bot.forward_message(
                    chat_id,
                    message.message_id,
                    ADMIN_CHAT_ID
                )

            except Exception as e:

                print(
                    "خطا در فوروارد رسید:",
                    e
                )

            await send_receipt_received_message(
                message,
                order
            )

            return

        # رسید متنی
        if text:

            order["receipt"] = text
            order["step"] = "waiting_confirmation"
            order["status"] = "waiting_confirmation"

            await notify_admin(
                bot,
                message,
                order
            )

            await send_receipt_received_message(
                message,
                order
            )

            return

        return

    if not text:
        return

    # =====================================================
    # جم با آیدی - دریافت آیدی
    # =====================================================

    if step == "account_id":

        order["account_id"] = text
        order["step"] = "account_name"

        await message.reply(
            "👤 لطفاً اسم اکانت خود را ارسال کنید:"
        )

        return

    # =====================================================
    # جم با آیدی - دریافت اسم
    # =====================================================

    if step == "account_name":

        order["account_name"] = text

        await send_payment_info(
            message,
            order
        )

        return

    # =====================================================
    # جم اطلاعات - Gmail
    # =====================================================

    if step == "gmail":

        order["gmail"] = text
        order["step"] = "support_info"

        await message.reply(
            "📌 لطفاً اطلاعات غیرحساس موردنیاز "
            "سفارش را ارسال کنید:"
        )

        return

    # =====================================================
    # جم اطلاعات - اطلاعات پشتیبانی
    # =====================================================

    if step == "support_info":

        order["support_info"] = text
        order["step"] = "support_image"

        await message.reply(
            "📸 لطفاً شات 10 تایی پشتیبانی "
            "را به صورت تصویر ارسال کنید:"
        )

        return

    # =====================================================
    # جم اطلاعات - اسم اکانت
    # =====================================================

    if step == "account_name_info":

        order["account_name"] = text
        order["step"] = "account_id_info"

        await message.reply(
            "🆔 لطفاً آیدی اکانت خود را ارسال کنید:"
        )

        return

    # =====================================================
    # جم اطلاعات - آیدی اکانت
    # =====================================================

    if step == "account_id_info":

        order["account_id"] = text

        await send_payment_info(
            message,
            order
        )

        return


# =========================================================
# دریافت تصویر شات پشتیبانی
# =========================================================

@bot.on_message()
async def support_image_handler(
    bot: Robot,
    message: Message
):

    chat_id = message.chat_id

    if chat_id not in pending_orders:
        return

    order = pending_orders[chat_id]

    if order.get("step") != "support_image":
        return

    file_data = getattr(
        message,
        "file",
        None
    )

    if not file_data:
        return

    # نگهداری خود فایل برای تشخیص دریافت
    order["support_image"] = file_data

    # مهم:
    # message_id تصویر ذخیره می‌شود تا همان تصویر
    # مستقیماً برای مدیر فوروارد شود.
    order["support_image_message_id"] = message.message_id

    order["step"] = "account_name_info"

    await message.reply(
        "📸 شات پشتیبانی دریافت شد ✅\n\n"
        "👤 لطفاً اسم اکانت خود را ارسال کنید:"
    )


# =========================================================
# پیام دریافت رسید + کد پیگیری
# =========================================================

async def send_receipt_received_message(
    message,
    order
):

    tracking_code = order["tracking_code"]

    await message.reply(
        "🧾 رسید پرداخت شما دریافت شد ✅\n\n"
        "📦 سفارش شما با موفقیت ثبت شد.\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "⏳ وضعیت سفارش شما:\n"
        "در انتظار تأیید رسید\n\n"

        f"🎫 کد پیگیری سفارش:\n"
        f"{tracking_code}\n\n"

        "💎 لطفاً این کد پیگیری را نزد خود نگه دارید.\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "🙏 ممنون از اعتماد شما به TRIX SHOP ❤️"
    )


# =========================================================
# ارسال اطلاعات کارت
# =========================================================

async def send_payment_info(
    message,
    order
):

    order["step"] = "receipt"
    order["status"] = "receipt"

    package = order["package"]

    await message.reply(
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

        "🧾 سپس رسید پرداخت را "
        "به صورت تصویر یا متن ارسال کنید."
    )


# =========================================================
# اطلاع سفارش به مدیر
# =========================================================

async def notify_admin(
    bot,
    message,
    order
):

    package = order["package"]
    tracking_code = order["tracking_code"]

    admin_text = (
        "🔔 سفارش جدید دریافت شد\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "🎫 کد پیگیری:\n"
        f"{tracking_code}\n\n"

        "💎 محصول:\n"
        f"{package['name']}\n\n"

        "💰 مبلغ:\n"
        f"{package['price']}\n\n"

        "🆔 شناسه چت مشتری:\n"
        f"{message.chat_id}\n\n"
    )

    # =====================================================
    # اطلاعات تکمیل‌شده سفارش جم اطلاعات
    # =====================================================

    if order.get("gmail"):

        admin_text += (
            "📧 Gmail مشتری:\n"
            f"{order['gmail']}\n\n"
        )

    if order.get("support_info"):

        admin_text += (
            "📌 اطلاعات پشتیبانی:\n"
            f"{order['support_info']}\n\n"
        )

    if order.get("account_name"):

        admin_text += (
            "👤 اسم اکانت مشتری:\n"
            f"{order['account_name']}\n\n"
        )

    if order.get("account_id"):

        admin_text += (
            "🆔 آیدی اکانت مشتری:\n"
            f"{order['account_id']}\n\n"
        )

    # =====================================================
    # رمز جیمیل عمداً دریافت یا ارسال نمی‌شود
    # =====================================================

    admin_text += (
        "🔐 رمز جیمیل:\n"
        "دریافت نمی‌شود 🔒\n\n"
    )

    # =====================================================
    # وضعیت شات پشتیبانی
    # =====================================================

    if order.get("support_image_message_id"):

        admin_text += (
            "📸 شات 10 تایی پشتیبانی:\n"
            "تصویر دریافت شد و در ادامه فوروارد می‌شود ✅\n\n"
        )

    # =====================================================
    # رسید پرداخت
    # =====================================================

    admin_text += (
        "🧾 رسید پرداخت:\n"
        "دریافت شد ✅\n\n"

        "⏳ وضعیت:\n"
        "در انتظار بررسی رسید\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "⬇️ لطفاً وضعیت رسید را مشخص کنید."
    )

    try:

        # -------------------------------------------------
        # ارسال متن کامل اطلاعات سفارش به مدیر
        # -------------------------------------------------

        await bot.send_message(
            ADMIN_CHAT_ID,
            admin_text,
            chat_keypad=admin_receipt_keypad(
                tracking_code
            ),
            chat_keypad_type="New"
        )

        # -------------------------------------------------
        # ارسال مستقیم عکس شات 10 تایی پشتیبانی
        # -------------------------------------------------

        if order.get("support_image_message_id"):

            try:

                await bot.forward_message(
                    message.chat_id,
                    order["support_image_message_id"],
                    ADMIN_CHAT_ID
                )

                await bot.send_message(
                    ADMIN_CHAT_ID,
                    "📸 شات 10 تایی کدهای پشتیبانی سفارش بالا است.\n\n"
                    f"🎫 کد پیگیری: {tracking_code}"
                )

            except Exception as image_error:

                print(
                    "خطا در فوروارد شات پشتیبانی:",
                    image_error
                )

    except Exception as e:

        print(
            "خطا در ارسال سفارش به مدیر:",
            e
        )


# =========================================================
# دکمه‌ها
# =========================================================

@bot.on_callback()
async def all_callbacks(
    bot: Robot,
    message: Message
):

    try:

        button_id = message.aux_data.button_id

    except Exception as e:

        print(
            "خطا در دریافت button_id:",
            e
        )

        return

    if not button_id:
        return

    chat_id = message.chat_id

    print(
        f"[CALLBACK] chat_id={chat_id} | button_id={button_id}"
    )

    # =====================================================
    # امنیت: دکمه‌های مدیریتی فقط برای مالک
    # =====================================================

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

    # =====================================================
    # خرید
    # =====================================================

    if button_id == "buy":

        await message.reply_keypad(
            "🛍 لیست جم با ایدی : 💎\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page1_keypad()
        )

        return

    # =====================================================
    # صفحه دوم
    # =====================================================

    if button_id == "next_page":

        await message.reply_keypad(
            "🛍 لیست جم با اطلاعات : 📌\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page2_keypad()
        )

        return

    # =====================================================
    # صفحه اول
    # =====================================================

    if button_id == "back_page":

        await message.reply_keypad(
            "🛍 لیست جم با ایدی : 💎\n\n"
            "بسته موردنظر را انتخاب کنید:",
            page1_keypad()
        )

        return

    # =====================================================
    # لغو سفارش
    # =====================================================

    if button_id == "cancel_order":

        if chat_id in pending_orders:

            old_order = pending_orders.pop(chat_id)

            old_tracking = old_order.get(
                "tracking_code"
            )

            if old_tracking:

                orders_by_tracking.pop(
                    old_tracking,
                    None
                )

        await message.reply_keypad(
            "❌ سفارش لغو شد.\n\n"
            "🛍 می‌توانید دوباره یک بسته انتخاب کنید:",
            page1_keypad()
        )

        return

    # =====================================================
    # انتخاب بسته
    # =====================================================

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

    # =====================================================
    # تأیید سفارش اولیه
    # =====================================================

    if button_id.startswith("confirm_"):

        package_id = button_id.replace(
            "confirm_",
            "",
            1
        )

        if package_id not in PACKAGES:
            return

        package = PACKAGES[package_id]

        tracking_code = generate_tracking_code()

        order = {
            "package": package,
            "package_id": package_id,
            "tracking_code": tracking_code,
            "step": None,
            "status": "information"
        }

        # ذخیره سفارش مشتری
        pending_orders[chat_id] = order

        # ذخیره مستقیم با کد پیگیری
        orders_by_tracking[tracking_code] = {
            "customer_chat_id": chat_id,
            "order": order
        }

        # =================================================
        # جم با آیدی
        # =================================================

        if package["type"] == "id":

            order["step"] = "account_id"

            await message.reply(
                "🆔 لطفاً آیدی اکانت خود را ارسال کنید:"
            )

            return

        # =================================================
        # جم اطلاعات
        # =================================================

        if package["type"] == "info":

            order["step"] = "gmail"

            await message.reply(
                "سفارش شما تایید شد ✅\n\n"

                "💎 نوع سفارش:\n"
                f"{package['name']}\n\n"

                "💰 قیمت:\n"
                f"{package['price']}\n\n"

                "📧 جی‌میل:\n"
                "[ ]\n\n"

                "🗳️ رمز جیمیل:\n"
                "[ ]\n\n"

                "📸 شات 10 تایی پشتیبانی:\n"
                "[ ]\n\n"

                "👤 اسم اکانت:\n"
                "[ ]\n\n"

                "🆔 ایدی اکانت:\n"
                "[ ]"   
            )

            return

    # =====================================================
    # تأیید رسید توسط مالک
    # =====================================================

    if button_id.startswith("approve_receipt_"):

        tracking_code = button_id.replace(
            "approve_receipt_",
            "",
            1
        )

        customer_chat_id, order = find_order_by_tracking(
            tracking_code
        )

        if not order:

            await message.reply(
                "❌ سفارش موردنظر پیدا نشد.\n\n"
                "ممکن است این سفارش مربوط به قبل از اجرای "
                "نسخه جدید ربات باشد."
            )

            return

        if order.get("status") != "waiting_confirmation":

            await message.reply(
                "⚠️ این رسید قبلاً بررسی شده است."
            )

            return

        # تغییر وضعیت
        order["status"] = "in_progress"
        order["step"] = "in_progress"

        package = order["package"]

        # -------------------------------------------------
        # پیام تأیید برای مشتری
        # -------------------------------------------------

        try:

            await bot.send_message(
                customer_chat_id,

                "✅ رسید پرداخت شما تأیید شد.\n\n"

                "🔄 وضعیت سفارش شما:\n"
                "در حال انجام سفارش\n\n"

                "━━━━━━━━━━━━━━\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "💎 لطفاً منتظر تکمیل سفارش باشید.\n\n"

                "🙏 ممنون از اعتماد شما به TRIX SHOP ❤️"
            )

        except Exception as e:

            print(
                "خطا در ارسال تأیید به مشتری:",
                e
            )

        # -------------------------------------------------
        # پیام جدید برای مالک + دکمه تکمیل سفارش
        # -------------------------------------------------

        try:

            await bot.send_message(
                ADMIN_CHAT_ID,

                "✅ رسید سفارش تأیید شد.\n\n"

                "━━━━━━━━━━━━━━\n\n"

                "💎 بسته:\n"
                f"{package['name']}\n\n"

                "💰 قیمت:\n"
                f"{package['price']}\n\n"

                "🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "🔄 وضعیت:\n"
                "در حال انجام سفارش\n\n"

                "━━━━━━━━━━━━━━\n\n"

                "بعد از انجام سفارش برای مشتری، "
                "دکمه زیر را بزنید:",

                chat_keypad=admin_done_keypad(
                    tracking_code
                ),

                chat_keypad_type="New"
            )

        except Exception as e:

            print(
                "خطا در ارسال دکمه تکمیل سفارش:",
                e
            )

        return

    # =====================================================
    # رد رسید توسط مالک
    # =====================================================

    if button_id.startswith("reject_receipt_"):

        tracking_code = button_id.replace(
            "reject_receipt_",
            "",
            1
        )

        customer_chat_id, order = find_order_by_tracking(
            tracking_code
        )

        if not order:

            await message.reply(
                "❌ سفارش موردنظر پیدا نشد.\n\n"
                "ممکن است این سفارش مربوط به قبل از اجرای "
                "نسخه جدید ربات باشد."
            )

            return

        if order.get("status") != "waiting_confirmation":

            await message.reply(
                "⚠️ این رسید قبلاً بررسی شده است."
            )

            return

        # ثبت اینکه مدیر باید توضیح این سفارش را بفرستد
        admin_reject_waiting[ADMIN_CHAT_ID] = tracking_code

        await message.reply(
            "❌ رد رسید انتخاب شد.\n\n"

            "📝 لطفاً دلیل یا توضیحات رد شدن رسید "
            "را در پیام بعدی ارسال کنید.\n\n"

            "📨 متن شما مستقیماً برای مشتری ارسال خواهد شد."
        )

        return

    # =====================================================
    # تکمیل سفارش توسط مالک
    # =====================================================

    if button_id.startswith("order_done_"):

        tracking_code = button_id.replace(
            "order_done_",
            "",
            1
        )

        customer_chat_id, order = find_order_by_tracking(
            tracking_code
        )

        if not order:

            await message.reply(
                "❌ سفارش موردنظر پیدا نشد.\n\n"
                "ممکن است این سفارش مربوط به قبل از اجرای "
                "نسخه جدید ربات باشد."
            )

            return

        if order.get("status") != "in_progress":

            await message.reply(
                "⚠️ این سفارش هنوز در وضعیت "
                "در حال انجام سفارش نیست."
            )

            return

        # تغییر وضعیت به تکمیل شده
        order["status"] = "completed"
        order["step"] = "completed"

        package = order["package"]

        # -------------------------------------------------
        # پیام نهایی برای مشتری
        # -------------------------------------------------

        final_message = (
            "🎉 سفارش شما تکمیل شد ✅\n\n"

            f"💎 بسته:\n"
            f"{package['name']}\n\n"

            f"💰 قیمت:\n"
            f"{package['price']}\n\n"

            f"🎫 کد پیگیری:\n"
            f"{tracking_code}\n\n"

            "━━━━━━━━━━━━━━\n\n"

            "✅ سفارش شما با موفقیت انجام شد.\n\n"

            "ممنونم بابت انتخابتون\n"
            "𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏 ❤️"
        )

        try:

            await bot.send_message(
                customer_chat_id,
                final_message
            )

        except Exception as e:

            print(
                "خطا در ارسال پیام تکمیل سفارش:",
                e
            )

            await message.reply(
                "⚠️ سفارش تکمیل شد، اما ارسال پیام "
                "به مشتری با خطا مواجه شد."
            )

            return

        await message.reply(
            "🎉 سفارش با موفقیت تکمیل شد.\n\n"

            f"💎 بسته: {package['name']}\n"
            f"💰 قیمت: {package['price']}\n"
            f"🎫 کد پیگیری: {tracking_code}"
        )

        return

    # =====================================================
    # پیگیری سفارش
    # =====================================================

    if button_id == "orders":

        if chat_id in pending_orders:

            order = pending_orders[chat_id]

            status_value = order.get(
                "status",
                ""
            )

            if status_value == "waiting_confirmation":

                status = (
                    "⏳ در انتظار تأیید رسید"
                )

            elif status_value == "in_progress":

                status = (
                    "🔄 در حال انجام سفارش"
                )

            elif status_value == "rejected":

                status = (
                    "❌ رسید رد شده"
                )

            elif status_value == "completed":

                status = (
                    "✅ تکمیل شده"
                )

            else:

                status = (
                    "⏳ در حال تکمیل اطلاعات"
                )

            await message.reply(
                "📦 سفارش فعال شما\n\n"

                "━━━━━━━━━━━━━━\n\n"

                "🎫 کد پیگیری:\n"
                f"{order['tracking_code']}\n\n"

                "💎 محصول:\n"
                f"{order['package']['name']}\n\n"

                "💰 مبلغ:\n"
                f"{order['package']['price']}\n\n"

                "📌 وضعیت:\n"
                f"{status}\n\n"

                "━━━━━━━━━━━━━━"
            )

        else:

            await message.reply(
                "📦 در حال حاضر سفارش فعالی "
                "برای شما پیدا نشد."
            )

        return

    # =====================================================
    # پشتیبانی
    # =====================================================

    if button_id == "support":

        await message.reply(
            "🆘 برای پشتیبانی با مدیر فروشگاه "
            "در ارتباط باشید."
        )

        return


# =========================================================
# اجرای ربات
# =========================================================

bot.run()
