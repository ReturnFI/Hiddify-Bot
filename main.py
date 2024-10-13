# main.py
import telebot
from telebot import types
from utils.add_user import add_user_name
from utils.show_user import show_user, delete_user_success, inline_query
from utils.serverinfo import get_server_info
from utils.backup import backup
from utils.authorization import is_authorized_user
from utils.help import help_command
from utils.admins import show_admins_menu, show_admin_list, delete_admins_user, process_admin_deletion
from utils.lang import lang
from utils.api import HiddifyApi

hiddify_api = HiddifyApi()

bot = telebot.TeleBot(hiddify_api.telegram_token)

main_menu_markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    main_menu_markup.keyboard.clear()
    if is_authorized_user(message.from_user.id):
        main_menu_markup.add(lang.get_string("FA", "ADDUSER"), lang.get_string("FA", "SHOWUSER"))
        main_menu_markup.add(lang.get_string("FA", "SERVERINFO"), lang.get_string("FA", "BACKUP"))
        main_menu_markup.add(lang.get_string("FA", "ADMIN"))
    else:
        main_menu_markup.add(lang.get_string("FA", "HELP"), lang.get_string("FA", "SHOWUSER"))
    
    bot.reply_to(message, lang.get_string("FA", "START"), reply_markup=main_menu_markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == lang.get_string("FA", "SHOWUSER"):
        bot.reply_to(message, lang.get_string("FA", "UUID"))
        bot.register_next_step_handler(message, show_user, bot)
    elif message.text == lang.get_string("FA", "HELP"):
        help_command(bot, message)
    elif is_authorized_user(message.from_user.id):
        if message.text == lang.get_string("FA", "ADDUSER"):
            add_user_name(bot, message)
        elif message.text == lang.get_string("FA", "ADMIN"):
            show_admins_menu(bot, message)
        elif message.text == lang.get_string("FA", "SERVERINFO"):
            get_server_info(bot, message)
        elif message.text == lang.get_string("FA", "BACKUP"):
            backup(bot, message)
        elif message.text == lang.get_string("FA", "BACKMAINMENU"):
            send_welcome(message)
        elif message.text == lang.get_string("FA", "SHOWADMIN"):
            show_admin_list(bot, message)
        elif message.text == lang.get_string("FA", "DELETEADMIN"):
            delete_admins_user(bot, message)
        else:
            bot.reply_to(message, lang.get_string("FA", "ERORR"), reply_markup=main_menu_markup)
    else:
        bot.reply_to(message, lang.get_string("FA", "UNAUTHORIZED"))

@bot.inline_handler(lambda query: query.query.strip() != "")
def handle_inline_query(query):
    if is_authorized_user(query.from_user.id):
        results = inline_query(query.query)
        if results:
            bot.answer_inline_query(query.id, results, cache_time=5)
    else:
        unauthorized_message = types.InlineQueryResultArticle(
            id=lang.get_string("FA", "AUTHORIZED"),
            title=lang.get_string("FA", "AUTHORIZED"),
            description=lang.get_string("FA", "UNAUTHORIZED"),
            input_message_content=types.InputTextMessageContent(lang.get_string("FA", "UNAUTHORIZED"))
        )
        bot.answer_inline_query(query.id, [unauthorized_message], cache_time=5)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    action, uuid = call.data.split(":")
    if action == "delete":
        hiddify_api.delete_user(uuid)
        delete_user_success(bot, call.message.chat.id, call.message.message_id)
    elif action == "reset_user":
        hiddify_api.reset_user_last_reset_time(uuid)
        bot.answer_callback_query(call.id, lang.get_string("FA", "RESET"))
    elif action == "reset_days":
        hiddify_api.update_package_days(uuid)
        bot.answer_callback_query(call.id, lang.get_string("FA", "RESETTIME"))
    elif action == "reset_traffic":
        hiddify_api.update_traffic(uuid)
        bot.answer_callback_query(call.id, lang.get_string("FA", "RESETGB"))

bot.polling()
