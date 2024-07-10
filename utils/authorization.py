from utils.api import HiddifyApi

hiddify_api = HiddifyApi()

def is_authorized_user(user_id):
    """Check if the user is authorized."""
    return user_id in hiddify_api.allowed_user_ids
