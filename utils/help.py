# help.py

import requests
from telebot import types
from utils.lang import lang
from utils.api import HiddifyApi

hiddify_api = HiddifyApi()

def help_command(bot, message):
    uuid_prompt_text = lang.get_string("FA", "UUID")
    bot.reply_to(message, uuid_prompt_text)
    bot.register_next_step_handler(message, lambda msg: send_app_information(msg, bot))

def send_app_information(message, bot):
    try:
        uuid = message.text
        app_information = hiddify_api.get_app_information(uuid)

        if app_information:
            app_info_text = "\n\n"
            for app in app_information:
                app_name = app.get('title', 'N/A')
                if app_name in ["V2RayNG", "Hiddify Next", "Streisand"]:
                    app_info_text += f"*Name:* {app_name}\n"
                    app_info_text += f"*Guide URL:* [Watch Video]({app.get('guide_url', 'N/A')})\n"
                    app_info_text += "*Installation Options:*\n"
                    install_options = app.get('install', [])
                    for i, install_option in enumerate(install_options, start=1):
                        install_type = install_option.get('type', 'N/A')
                        install_url = install_option.get('url', 'N/A')
                        app_info_text += f"{i}. [{install_type}]({install_url})\n"
                    app_info_text += "\n"
            
            bot.send_message(message.chat.id, app_info_text, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Failed to fetch app information.")
    except Exception as e:
        print(f"Error in send_app_information: {e}")
        bot.send_message(message.chat.id, "An error occurred while processing your request.")