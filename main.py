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

pending_orders = {}

# کدهای پیگیری قبلی برای جلوگیری از تکراری شدن
used_tracking_codes = set()

# سفارش‌هایی که مدیر برای رد کردنشان منتظر توضیح است
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
                text="📌 هفتگی 450 جم — 369.000T💸"
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
# دکمه تأیید و لغو
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
# دکمه‌های مدیر برای رسید
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
# دکمه انجام شد برای مدیر
# =========================================================

def admin_done_keypad(tracking_code):
    builder = ChatKeypadBuilder()

    return (
        builder
        .row(
            builder.button(
                id=f"order_done_{tracking_code}",
                text="✅ انجام شد"
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
        "price": "549💸",
        "type": "id"
    },

    "info_weekly": {
        "name": "هفتگی (450 جم)",
        "price": "369.000T💸",
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
# پیدا کردن سفارش با کد پیگیری
# =========================================================

def find_order_by_tracking(tracking_code):
    for customer_chat_id, order in pending_orders.items():
        if order.get("tracking_code") == tracking_code:
            return customer_chat_id, order

    return None, None


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
    # توضیح رد رسید توسط مدیر
    # =====================================================

    if chat_id == ADMIN_CHAT_ID and chat_id in admin_reject_waiting:

        tracking_code = admin_reject_waiting.pop(chat_id)

        customer_chat_id, order = find_order_by_tracking(
            tracking_code
        )

        if not order:
            await message.reply(
                "❌ سفارش موردنظر پیدا نشد."
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

        # ارسال توضیح رد برای مشتری
        try:
            await bot.send_message(
                customer_chat_id,
                "❌ رسید پرداخت شما رد شد.\n\n"
                "📌 توضیح مدیر:\n"
                f"{text}\n\n"
                "━━━━━━━━━━━━━━\n\n"
                f"🎫 کد پیگیری:\n{tracking_code}"
            )
        except Exception as e:
            print(
                "خطا در ارسال دلیل رد به مشتری:",
                e
            )

        await message.reply(
            "❌ رسید رد شد و توضیح آن برای مشتری ارسال شد."
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

    order["support_image"] = file_data
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

    if order.get("account_id"):

        admin_text += (
            "🎮 آیدی اکانت:\n"
            f"{order['account_id']}\n\n"
        )

    if order.get("account_name"):

        admin_text += (
            "👤 نام اکانت:\n"
            f"{order['account_name']}\n\n"
        )

    if order.get("gmail"):

        admin_text += (
            "📧 Gmail:\n"
            f"{order['gmail']}\n\n"
        )

    if order.get("support_info"):

        admin_text += (
            "📌 اطلاعات پشتیبانی:\n"
            f"{order['support_info']}\n\n"
        )

    if order.get("support_image"):

        admin_text += (
            "📸 شات پشتیبانی:\n"
            "دریافت شد ✅\n\n"
        )

    admin_text += (
        "🧾 رسید پرداخت:\n"
        "دریافت شد ✅\n\n"

        "⏳ وضعیت:\n"
        "در انتظار بررسی رسید\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "⬇️ لطفاً وضعیت رسید را مشخص کنید."
    )

    try:

        await bot.send_message(
            ADMIN_CHAT_ID,
            admin_text,
            chat_keypad=admin_receipt_keypad(
                tracking_code
            ),
            chat_keypad_type="New"
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

        button_id = (
            message
            .aux_data
            .button_id
        )

    except Exception:

        return

    chat_id = message.chat_id

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

            del pending_orders[chat_id]

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

            "آیا این بسته را تأیید می‌کنید؟",
            order_keypad(button_id)
        )

        return

    # =====================================================
    # تأیید سفارش
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

        pending_orders[chat_id] = {
            "package": package,
            "package_id": package_id,
            "tracking_code": tracking_code,
            "step": None,
            "status": "information"
        }

        # =================================================
        # جم با آیدی
        # =================================================

        if package["type"] == "id":

            pending_orders[chat_id]["step"] = (
                "account_id"
            )

            await message.reply(
                "🆔 لطفاً آیدی اکانت خود را ارسال کنید:"
            )

            return

        # =================================================
        # جم اطلاعات
        # =================================================

        if package["type"] == "info":

            pending_orders[chat_id]["step"] = (
                "gmail"
            )

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
    # تأیید رسید توسط مدیر
    # =====================================================

    if button_id.startswith("approve_receipt_"):

        if chat_id != ADMIN_CHAT_ID:
            return

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
                "❌ سفارش موردنظر پیدا نشد."
            )
            return

        if order.get("status") != "waiting_confirmation":

            await message.reply(
                "⚠️ این رسید قبلاً بررسی شده است."
            )
            return

        order["status"] = "in_progress"
        order["step"] = "in_progress"

        # پیام به مشتری
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

        # دکمه انجام شد برای مدیر
        try:

            await bot.send_message(
                ADMIN_CHAT_ID,

                "✅ رسید این سفارش تأیید شد.\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "🔄 وضعیت سفارش:\n"
                "در حال انجام سفارش\n\n"

                "بعد از انجام سفارش، دکمه زیر را بزنید:",

                chat_keypad=admin_done_keypad(
                    tracking_code
                ),
                chat_keypad_type="New"
            )

        except Exception as e:

            print(
                "خطا در ارسال دکمه انجام شد:",
                e
            )

        return

    # =====================================================
    # رد رسید توسط مدیر
    # =====================================================

    if button_id.startswith("reject_receipt_"):

        if chat_id != ADMIN_CHAT_ID:
            return

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
                "❌ سفارش موردنظر پیدا نشد."
            )
            return

        if order.get("status") != "waiting_confirmation":

            await message.reply(
                "⚠️ این رسید قبلاً بررسی شده است."
            )
            return

        admin_reject_waiting[ADMIN_CHAT_ID] = tracking_code

        await message.reply(
            "❌ رد رسید انتخاب شد.\n\n"
            "📝 لطفاً توضیحات رد شدن رسید را "
            "در پیام بعدی ارسال کنید.\n\n"
            "توضیح شما مستقیماً برای مشتری ارسال می‌شود."
        )

        return

    # =====================================================
    # انجام شد توسط مدیر
    # =====================================================

    if button_id.startswith("order_done_"):

        if chat_id != ADMIN_CHAT_ID:
            return

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
                "❌ سفارش موردنظر پیدا نشد."
            )
            return

        if order.get("status") != "in_progress":

            await message.reply(
                "⚠️ این سفارش در وضعیت قابل تکمیل نیست."
            )
            return

        order["status"] = "completed"
        order["step"] = "completed"

        package = order["package"]

        # پیام نهایی برای مشتری
        try:

            await bot.send_message(
                customer_chat_id,

                "🎉 سفارش شما تکمیل شد ✅\n\n"

                "💎 بسته:\n"
                f"{package['name']}\n\n"

                "💰 قیمت:\n"
                f"{package['price']}\n\n"

                f"🎫 کد پیگیری:\n"
                f"{tracking_code}\n\n"

                "━━━━━━━━━━━━━━\n\n"

                "✅ سفارش شما با موفقیت انجام شد.\n\n"

                "ممنونم بابت انتخابتون\n"
                "𝐓𝐑𝐈𝐗 𝐒𝐇𝐎𝐏 ❤️"
            )

        except Exception as e:

            print(
                "خطا در ارسال تکمیل سفارش:",
                e
            )

        await message.reply(
            "🎉 سفارش با موفقیت تکمیل شد.\n\n"
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
