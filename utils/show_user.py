from datetime import datetime, timedelta
from telebot import types
from utils.api import HiddifyApi
from utils.lang import lang
from utils.authorization import is_authorized_user

hiddify_api = HiddifyApi()

def format_user_info(user_data, uuid):
    current_usage_gb = "{:.2f}".format(user_data.get('current_usage_GB', 0))
    last_online_display, last_online_str = parse_online_status(user_data)
    start_date = user_data.get('start_date')

    if start_date:
        return (
            f"Name: {user_data.get('name', 'N/A')}\n"
            f"Usage Limit: {user_data.get('usage_limit_GB', 'N/A')} GB\n"
            f"Current Usage: {current_usage_gb} GB\n"
            f"Online: {last_online_display}\n"
            f"Last Online: {last_online_str}\n"
            f"Package Days: {user_data.get('package_days', 'N/A')}\n"
            f"Start Date: {start_date}"
        )
    else:
        return (
            f"UUID: {uuid}\n"
            f"Name: {user_data.get('name', 'N/A')}\n"
            f"Usage Limit: {user_data.get('usage_limit_GB', 'N/A')} GB\n"
            f"Package Days: {user_data.get('package_days', 'N/A')}\n"
            "❌ User not active ❌"
        )

def parse_online_status(user_data):
    current_time = datetime.now()
    last_online_str = user_data.get('last_online', 'N/A')

    try:
        if last_online_str != 'N/A':
            last_online = datetime.strptime(last_online_str, '%Y-%m-%d %H:%M:%S')
            time_diff = current_time - last_online
            return ("🟢" if time_diff < timedelta(minutes=1) else "🔴"), last_online_str
    except ValueError:
        pass 

    return "❌", last_online_str

def create_inline_buttons(uuid, user_authorized):
    web_app_info = types.WebAppInfo(url=f"{hiddify_api.sublinkurl}{uuid}/")
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if user_authorized:
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Delete", callback_data=f"delete:{uuid}"),
            types.InlineKeyboardButton(text="Reset User", callback_data=f"reset_user:{uuid}")
        )
        inline_keyboard.add(
            types.InlineKeyboardButton(text="Reset Days", callback_data=f"reset_days:{uuid}"),
            types.InlineKeyboardButton(text="Reset Traffic", callback_data=f"reset_traffic:{uuid}")
        )
    inline_keyboard.add(types.InlineKeyboardButton(text="Open Sublink", web_app=web_app_info))
    return inline_keyboard

def show_user(message, bot):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    uuid = message.text
    user_data = hiddify_api.find_service(uuid)
    
    if not user_data:
        bot.reply_to(message, lang.get_string("FA", "USERERROR"))
        return

    user_info = format_user_info(user_data, uuid)
    qr_code = hiddify_api.generate_qr_code(f"{hiddify_api.sublinkurl}{uuid}/")
    inline_buttons = create_inline_buttons(uuid, is_authorized_user(message.from_user.id))

    bot.send_photo(message.chat.id, qr_code, caption=user_info, reply_markup=inline_buttons)

def delete_user_success(bot, chat_id, message_id):
    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, "User deleted successfully")

def inline_query(query):
    MAX_RESULTS = 50 
    results = []

    if query.strip().lower().startswith("list"):
        query_name = query[5:].strip()
        user_list = hiddify_api.get_user_list_name(query_name)[:MAX_RESULTS]

        for user in user_list:
            results.append(format_inline_user_result(user))

    return results

def format_inline_user_result(user):
    user_uuid = user['uuid']
    user_name = user['name']
    package_days = user['package_days']
    usage_limit_gb = user['usage_limit_GB']
    current_usage_gb = user['current_usage_GB']
    last_online_str = user['last_online']
    last_online_formatted = format_last_online(last_online_str)
    
    title = f"{user_name}"
    description = f"Traffic Limit: {usage_limit_gb:.2f} GB, Package Days: {package_days}"
    response_text = (
        f"ID: `{user_uuid}`\n"
        f"Name: {user_name}\n"
        f"Package Days: {package_days}\n"
        f"Traffic: {current_usage_gb:.2f} / {usage_limit_gb} GB\n"
        f"Last Online: {last_online_formatted}\n"
        f"Subscription: [Subscription Link]({hiddify_api.sublinkurl}{user_uuid}/)"
    ).replace('.', '\\.')
    
    return types.InlineQueryResultArticle(
        id=user_uuid,
        title=title,
        description=description,
        url=f"{hiddify_api.sublinkurl}{user_uuid}/",
        input_message_content=types.InputTextMessageContent(response_text, parse_mode='MarkdownV2')
    )

def format_last_online(last_online_str):
    try:
        last_online = datetime.fromisoformat(last_online_str)
        return last_online.strftime('%Y/%m/%d %H:%M:%S')
    except (ValueError, TypeError):
        return "Not Active"
