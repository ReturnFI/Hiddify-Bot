from datetime import datetime, timedelta
from telebot import types
from utils.api import HiddifyApi
from utils.authorization import is_authorized_user

hiddify_api = HiddifyApi()

def show_user(message, bot):
    uuid = message.text
    user_data = hiddify_api.find_service(uuid)
    sent_message = None
    if user_data:
        current_time = datetime.now()
        last_online_str = user_data.get('last_online', 'N/A')
        start_date = user_data.get('start_date')
        
        if last_online_str != 'N/A':
            last_online = datetime.strptime(last_online_str, '%Y-%m-%d %H:%M:%S')
            time_diff = current_time - last_online
            if time_diff < timedelta(minutes=1):
                last_online_display = "🟢"
            else:
                last_online_display = "🔴"
        else:
            last_online_display = "❌"
        
        if start_date is not None:
            current_usage_gb = "{:.2f}".format(user_data.get('current_usage_GB', 0))
            user_info = (
                f"Name: {user_data.get('name', 'N/A')}\n"
                f"Usage Limit: {user_data.get('usage_limit_GB', 'N/A')} GB\n"
                f"Current Usage: {current_usage_gb} GB\n"
                f"Online: {last_online_display}\n"
                f"Last Online: {user_data.get('last_online', 'N/A')}\n"
                # f"Expiry Time: {user_data.get('expiry_time', 'N/A')}\n"
                f"Package Days: {user_data.get('package_days', 'N/A')}\n"
                f"Start Date: {start_date}"
            )
        else:
            user_info = (
                f"UUID: {uuid}\n"
                f"Name: {user_data.get('name', 'N/A')}\n"
                f"Usage Limit: {user_data.get('usage_limit_GB', 'N/A')} GB\n"
                f"Package Days: {user_data.get('package_days', 'N/A')}\n"
                "❌ User not active ❌"
            )
        
        sublink = f"{hiddify_api.sublinkurl}/{uuid}"
        qr_code = hiddify_api.generate_qr_code(sublink)
        web_app_info = types.WebAppInfo(url=sublink)
        if is_authorized_user(message.from_user.id):
            delete_button = types.InlineKeyboardButton(text="Delete", callback_data=f"delete:{uuid}")
            reset_user_button = types.InlineKeyboardButton(text="Reset User", callback_data=f"reset_user:{uuid}")
            reset_days_button = types.InlineKeyboardButton(text="Reset Days", callback_data=f"reset_days:{uuid}")
            reset_traffic_button = types.InlineKeyboardButton(text="Reset Traffic", callback_data=f"reset_traffic:{uuid}")
            
            inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
            inline_keyboard.add(delete_button, reset_user_button)
            inline_keyboard.add(reset_days_button, reset_traffic_button)
            inline_keyboard.add(types.InlineKeyboardButton(text="Open Sublink", web_app=web_app_info))
            
            sent_message = bot.send_photo(message.chat.id, qr_code, caption=user_info, reply_markup=inline_keyboard)
        else:
            unauthorized_keyboard = types.InlineKeyboardMarkup()
            unauthorized_keyboard.add(types.InlineKeyboardButton(text="Open Sublink", web_app=web_app_info))
            
            sent_message = bot.send_photo(message.chat.id, qr_code, caption=user_info, reply_markup=unauthorized_keyboard)
            if message.from_user.id not in hiddify_api.allowed_user_ids:
                hiddify_api.tele_id(uuid, message.from_user.id)
    else:
        bot.reply_to(message, "User not found.")

    return sent_message

def delete_user_success(bot, chat_id, message_id):
    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, "User deleted successfully")

def inline_query(query):
    results = []
    if query.strip().lower().startswith("list"):
        query_name = query[5:].strip()
        user_list = hiddify_api.get_user_list_name(query_name)

        if user_list:
            for user in user_list[:50]:
                user_uuid = user['uuid']
                user_name = user['name']
                package_days = user['package_days']
                usage_limit_gb = user['usage_limit_GB']
                current_usage_gb = user['current_usage_GB']
                last_online_str = user['last_online']

                if last_online_str:
                    try:
                        last_online = datetime.fromisoformat(last_online_str)
                        last_online_formatted = last_online.strftime('%Y/%m/%d %H:%M:%S')
                    except ValueError:
                        last_online_formatted = "Not Active"
                else:
                    last_online_formatted = "Not Active"

                title = f"{user_name}"
                discrip = f"Traffic Limit: {usage_limit_gb:.2f} GB\nPackage Days: {package_days}"
                subscription_link = f"{hiddify_api.sublinkurl}/{user_uuid}/"
                response_text = (
                    f"ID: `{user_uuid}`\n"
                    f"Name: {user_name}\n"
                    f"Package Days: {package_days}\n"
                    f"Traffic: {current_usage_gb:.2f} / {usage_limit_gb} GB\n"
                    f"Last Online: {last_online_formatted}\n"
                    f"Subscription: [Subscription Link]({subscription_link})"
                )
                response_text = response_text.replace('.', '\\.')

                article = types.InlineQueryResultArticle(
                    id=user_uuid,
                    title=title,
                    description=discrip,
                    url=subscription_link,
                    input_message_content=types.InputTextMessageContent(response_text, parse_mode='MarkdownV2')
                )
                results.append(article)
    return results
