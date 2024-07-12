import io
from datetime import datetime
from utils.api import HiddifyApi
from utils.lang import lang

hiddify_api = HiddifyApi()

def backup(bot, message):
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file_name = f"{current_datetime}.json"
    
    backup_data = hiddify_api.backup_file()
    if backup_data:
        backup_bytes_io = io.BytesIO(backup_data)
        backup_bytes_io.name = backup_file_name
        
        bot.send_document(message.chat.id, backup_bytes_io)
    else:
        bot.reply_to(message, lang.get_string("FA", "BACKUPERROR"))
