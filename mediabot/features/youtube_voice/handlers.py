from mediabot.env import TELEGRAM_PATH
from telegram import Update
from mediabot.context import Context
from pydub import AudioSegment
import speech_recognition as sr
from pathlib import Path
from telegram import File
from mediabot.features.track.model import Track
from mediabot.features.track.handlers import _track_search
from mediabot.features.advertisement.handlers import advertisement_message_send
from mediabot.features.advertisement.model import Advertisement


import pathlib
import secrets
import aiohttp
import asyncio
import shutil
import uuid
import os

def get_local_path_of(local_file: File):
    local_file_path = Path(*Path(local_file.file_path).parts[-3:])
    return Path(TELEGRAM_PATH, local_file_path)

recognizer = sr.Recognizer()

async def voice_convert(update: Update, context: Context):
    assert update.message and update.message.voice

    if update.message.voice.file_size >= 31457280:
        await update.message.reply_text("❌ Fayl juda katta.")
        return

    recognizer = sr.Recognizer()

    # Faylni olish
    voice_file = await context.bot.get_file(update.message.voice.file_id)
    local_voice_file_path = get_local_path_of(voice_file)
    print(f"[📥] Lokal fayl yo‘li: {local_voice_file_path}")

    # Vaqtinchalik fayl yaratish
    temp_file_path = Path("/media-service-files") / (secrets.token_hex(8) + ".oga")
    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(local_voice_file_path, temp_file_path)
    print(f"[✅] Fayl nusxalandi: {temp_file_path}")

    # WAV formatga o'tkazish
    wav_path = temp_file_path.with_suffix(".wav")
    audio = AudioSegment.from_file(temp_file_path)
    audio.export(wav_path, format="wav")
    print(f"[🔄] WAV fayl tayyor: {wav_path}")

    # Matnni ajratish
    try:
        with sr.AudioFile(str(wav_path)) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language="uz")
        print(f"[📝] Aniqlangan matn: {text}")

        # Qidiruvni amalga oshirish
        search_page = 0
        search_results_text, inline_keyboard_markup = await _track_search(
            context,
            text,
            search_page,
            update.effective_chat.id,
            update.effective_user.id
        )

        await advertisement_message_send(context, update.effective_chat.id, Advertisement.KIND_TRACK_SEARCH, \
         text=search_results_text, reply_markup=inline_keyboard_markup, reply_to_message_id=update.message.id)

    except Exception as e:
        print(f"[❌] Tanib olishda xatolik: {e}")
        await update.message.reply_text("❌ Ovozdan matn olinmadi.")

    finally:
        Path(local_voice_file_path).unlink(missing_ok=True)
        temp_file_path.unlink(missing_ok=True)
        wav_path.unlink(missing_ok=True)
        print("[🧹] Vaqtinchalik fayllar o‘chirildi.")
    

async def youtube_voice_handle_link_message(update: Update, context: Context) -> None:
    print("✅ Voice xabar qabul qilindi")
    await voice_convert(update, context)
