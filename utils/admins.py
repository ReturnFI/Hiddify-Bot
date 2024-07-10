# Admins.py
import telebot
from telebot import types
from utils.lang import lang
from utils.api import HiddifyApi
hiddify_api = HiddifyApi()

def show_admins_menu(bot, message):
    admins_menu_markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    admins_menu_markup.add(lang.get_string("FA", "ADDADMIN"), lang.get_string("FA", "SHOWADMIN"))
    admins_menu_markup.add(lang.get_string("FA", "DELETEADMIN"), lang.get_string("FA", "BACKMAINMENU"))

    bot.send_message(message.chat.id, lang.get_string("FA", "ADMINMENU"), reply_markup=admins_menu_markup)

def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

def show_admin_list(bot, message):
    admin_list = hiddify_api.get_admin_list()
    if admin_list:
        admin_list_text = "\n\n"
        for admin in admin_list:
            admin_list_text += f"Name: {escape_markdown_v2(admin['name'])}\n"
            admin_list_text += f"Mode: {escape_markdown_v2(admin['mode'])}\n"
            admin_list_text += f"Can Add Admin: {escape_markdown_v2(str(admin['can_add_admin']))}\n"
            admin_list_text += f"Max Users: {escape_markdown_v2(str(admin['max_users']))}\n"
            admin_list_text += f"UUID: `{escape_markdown_v2(admin['uuid'])}`\n"
            admin_list_text += "\n"
        bot.send_message(message.chat.id, admin_list_text, parse_mode='MarkdownV2')
    else:
        bot.send_message(message.chat.id, lang.get_string("FA", "ADMINFAI"))

def delete_admins_user(bot, message):
    bot.send_message(message.chat.id, lang.get_string("FA", "ADMINUUID"))
    bot.register_next_step_handler(message, lambda msg: process_admin_deletion(bot, msg))

def process_admin_deletion(bot, message):
    admin_uuid = message.text
    deleted = hiddify_api.delete_admin_user(admin_uuid)
    if deleted:
        bot.send_message(message.chat.id, lang.get_string("FA", "ADMINDELETED"))
    else:
        bot.send_message(message.chat.id, lang.get_string("FA", "ADMINNOTDELETED"))
