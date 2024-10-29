# serverinfo.py

from telebot import types
from utils.api import HiddifyApi

hiddify_api = HiddifyApi()

def get_server_info(bot, message):
    bot.send_chat_action(message.chat.id, 'typing')
    system_status = hiddify_api.get_system_status()
    if system_status:
        system_info = system_status.get('system', {})
        usage_history = system_status.get('usage_history', {})
        m5_online = usage_history.get('m5', {}).get('online', 'N/A')
        yesterday_online = usage_history.get('yesterday', {}).get('online', 'N/A')
        
        usage_today = int(usage_history.get('today', {}).get('usage', 0)) / (1024 ** 3)
        usage_yesterday = int(usage_history.get('yesterday', {}).get('usage', 0)) / (1024 ** 3)
        total_usage_bytes = int(usage_history.get('total', {}).get('usage', 0)) / (1024 ** 3)
        
        formatted_info = (
            f"CPU Percent: {system_info.get('cpu_percent', 'N/A')}% ⚠️\n"
            f"RAM Usage: {system_info.get('ram_used', 'N/A'):.2f}GB / {system_info.get('ram_total', 'N/A'):.2f}GB 〽️\n"
            f"Disk Usage: {system_info.get('disk_used', 'N/A'):.2f}GB / {system_info.get('disk_total', 'N/A'):.2f}GB 〽️\n"
            f"Total Usage: {total_usage_bytes:.2f} GB 🛜\n"
            f"----------------------------------\n"
            f"Yesterday Usage: {usage_yesterday:.2f} GB\n"
            f"Yesterday Online: {yesterday_online}\n"
            f"----------------------------------\n"
            f"Today Usage: {usage_today:.2f} GB\n"
            f"Users Online: {m5_online} 🟢"
        )
        bot.reply_to(message, formatted_info)
    else:
        bot.reply_to(message, "Failed to retrieve server status.")
