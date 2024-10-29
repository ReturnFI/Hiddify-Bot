# main.py
import telebot
from telebot import types
from telebot.util import async_dec
from utils import (
    add_user_name, show_user, delete_user_success, inline_query,
    get_server_info, backup, is_authorized_user, help_command,
    show_admins_menu, show_admin_list, delete_admins_user,
    lang, HiddifyApi
)

hiddify_api = HiddifyApi()
bot = telebot.TeleBot(hiddify_api.telegram_token)
main_menu_markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

def setup_main_menu(is_authorized):
    main_menu_markup.keyboard.clear()
    if is_authorized:
        main_menu_markup.add(
            lang.get_string("FA", "ADDUSER"),
            lang.get_string("FA", "SHOWUSER"),
            lang.get_string("FA", "SERVERINFO"),
            lang.get_string("FA", "BACKUP"),
            lang.get_string("FA", "ADMIN")
        )
    else:
        main_menu_markup.add(
            lang.get_string("FA", "HELP"),
            lang.get_string("FA", "SHOWUSER")
        )
    return main_menu_markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    authorized = is_authorized_user(user_id)
    setup_main_menu(authorized)
    bot.reply_to(message, lang.get_string("FA", "START"), reply_markup=main_menu_markup)

@bot.message_handler(func=lambda message: True)
@async_dec()
def handle_message(message):
    user_id = message.from_user.id
    text = message.text
    authorized = is_authorized_user(user_id)

    command_map = {
        lang.get_string("FA", "HELP"): lambda: help_command(bot, message),
        lang.get_string("FA", "ADDUSER"): lambda: add_user_name(bot, message),
        lang.get_string("FA", "ADMIN"): lambda: show_admins_menu(bot, message),
        lang.get_string("FA", "SERVERINFO"): lambda: get_server_info(bot, message),
        lang.get_string("FA", "BACKUP"): lambda: backup(bot, message),
        lang.get_string("FA", "BACKMAINMENU"): lambda: send_welcome(message),
        lang.get_string("FA", "SHOWADMIN"): lambda: show_admin_list(bot, message),
        lang.get_string("FA", "DELETEADMIN"): lambda: delete_admins_user(bot, message)
    }

    if text == lang.get_string("FA", "SHOWUSER"):
        bot.reply_to(message, lang.get_string("FA", "UUID"))
        bot.register_next_step_handler(message, show_user, bot)
    elif text in command_map and (authorized or text in [lang.get_string("FA", "HELP"), lang.get_string("FA", "SHOWUSER")]):
        command_map[text]()
    else:
        bot.reply_to(message, lang.get_string("FA", "UNAUTHORIZED" if not authorized else "ERORR"))


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
    action_map = {
        "delete": lambda: (hiddify_api.delete_user(uuid), delete_user_success(bot, call.message.chat.id, call.message.message_id)),
        "reset_user": lambda: (hiddify_api.reset_user_last_reset_time(uuid), bot.answer_callback_query(call.id, lang.get_string("FA", "RESET"))),
        "reset_days": lambda: (hiddify_api.update_package_days(uuid), bot.answer_callback_query(call.id, lang.get_string("FA", "RESETTIME"))),
        "reset_traffic": lambda: (hiddify_api.update_traffic(uuid), bot.answer_callback_query(call.id, lang.get_string("FA", "RESETGB")))
    }
    action_map.get(action, lambda: None)()

bot.polling(none_stop=True)
