# add_user.py

from telebot import types
from utils.api import HiddifyApi
from utils.lang import lang

hiddify_api = HiddifyApi()

def add_user_name(bot, message):
    bot.reply_to(message, lang.get_string("FA", "ADDNAME"))
    bot.register_next_step_handler(message, add_user_package_days, bot)

def add_user_package_days(message, bot):
    name = message.text
    bot.reply_to(message, lang.get_string("FA", "ADDDAYS"))
    bot.register_next_step_handler(message, validate_package_days, bot, name)

def validate_package_days(message, bot, name):
    if message.text.isnumeric():
        package_days = message.text
        bot.reply_to(message, lang.get_string("FA", "ADDGB"))
        bot.register_next_step_handler(message, validate_usage_limit, bot, name, package_days)
    else:
        bot.reply_to(message, lang.get_string("FA", "INVALIDDAYS"))
        bot.register_next_step_handler(message, validate_package_days, bot, name)

def validate_usage_limit(message, bot, name, package_days):
    try:
        usage_limit = float(message.text)
        add_user_complete(message, bot, name, package_days, usage_limit)
    except ValueError:
        bot.reply_to(message, lang.get_string("FA", "INVALIDGB"))
        bot.register_next_step_handler(message, validate_usage_limit, bot, name, package_days)

def add_user_complete(message, bot, name, package_days, usage_limit):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    uuid = hiddify_api.generate_uuid()
    telegram_id = message.chat.id
    success = hiddify_api.add_service(uuid, "", name, int(package_days), usage_limit, telegram_id)
    if success:
        user_data = hiddify_api.find_service(uuid)
        sublink_data = f"{hiddify_api.sublinkurl}{uuid}/"
        qr_code = hiddify_api.generate_qr_code(sublink_data)
        if user_data:
            user_info = (
                f"User UUID: {uuid}\n"
                f"Name: {user_data.get('name', 'N/A')}\n"
                f"Usage Limit: {user_data.get('usage_limit_GB', 'N/A')} GB\n"
                f"Package Days: {user_data.get('package_days', 'N/A')} Days"
            )
            inline_keyboard = types.InlineKeyboardMarkup()
            inline_keyboard.add(types.InlineKeyboardButton(text="Open Sublink", url=sublink_data))
            
            bot.send_photo(message.chat.id, qr_code, caption=user_info, reply_markup=inline_keyboard)
        else:
            bot.reply_to(message, "Failed to retrieve user data.")
    else:
        bot.reply_to(message, "Failed to add user.")
