from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mediabot.utils import chunks
import json


class TiktokMusicKeyboardMarkup:
    @staticmethod
    def get_music_button(data: str):
        data_type = "link" if data.startswith("http") else "file_id"
        payload = json.dumps({
            "type": data_type,
            "value": data,
        })
        keyboard = [
            [InlineKeyboardButton("🎵 Music", callback_data=f"tiktok_music12:{payload}")]
        ]
        return InlineKeyboardMarkup(keyboard)