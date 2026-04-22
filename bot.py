import telebot
from yt_dlp import YoutubeDL
import os
import threading

# تۆکنی بۆتەکەت لێرە دابنێ
API_TOKEN = '8229422475:AAHJE8xLFNDyTWzq6ktMZd2V6AIfXCsLjEw'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 سڵاو! لینکی هەر ڤیدیۆیەکم لە یوتیوب بۆ بنێرە، بە شێوەی (ڤیدیۆ) و (MP3) بۆت دادەگرم بەبێ کێشە.")

def process_link(message):
    url = message.text
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ چاوەڕێ بە... خەریکی هێنانم (ئەمە کەمێک کاتی دەوێت).")
    
    # ناوی جیاواز بۆ فایلەکان تا دوو کەس پێکەوە کێشەیان نەبێت
    video_name = f"video_{chat_id}.mp4"
    audio_name = f"audio_{chat_id}.mp3"

    # ڕێکخستنی داگرتنی ڤیدیۆ
    ydl_video = {
        'format': 'best',
        'outtmpl': video_name,
        'quiet': True,
        'noplaylist': True
    }
    
    # ڕێکخستنی داگرتنی دەنگ بە شێوەی MP3
    ydl_audio = {
        'format': 'bestaudio/best',
        'outtmpl': audio_name,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True
    }

    try:
        # ١. داگرتن و ناردنی MP3
        with YoutubeDL(ydl_audio) as ydl:
            ydl.download([url])
        with open(audio_name, 'rb') as audio:
            bot.send_audio(chat_id, audio, caption="🎵 فایلی MP3")
        if os.path.exists(audio_name):
            os.remove(audio_name)

        # ٢. داگرتن و ناردنی ڤیدیۆ
        with YoutubeDL(ydl_video) as ydl:
            ydl.download([url])
        with open(video_name, 'rb') as video:
            bot.send_video(chat_id, video, caption="🎬 فایلی ڤیدیۆ")
        if os.path.exists(video_name):
            os.remove(video_name)

        # سڕینەوەی نامەی چاوەڕێبە دوای تەواوبوون
        bot.delete_message(chat_id, msg.message_id) 

    except Exception as e:
        bot.send_message(chat_id, "❌ ببورە، کێشەیەک ڕوویدا. دڵنیابە لینکەکە ڕاستە و ڤیدیۆکە زۆر درێژ نییە.")
        # سڕینەوەی فایلە نیوەناقڵەکان ئەگەر هەڵەیەک ڕوویدا
        if os.path.exists(video_name): os.remove(video_name)
        if os.path.exists(audio_name): os.remove(audio_name)

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_url(message):
    # کارپێکردنی Thread بۆ ئەوەی بۆتەکە بۆ کەسانی تر نەوەستێت
    thread = threading.Thread(target=process_link, args=(message,))
    thread.start()

@bot.message_handler(func=lambda message: True)
def fallback(message):
    if not message.text.startswith('/'):
        bot.reply_to(message, "⚠️ تکایە تەنها لینکی یوتیوب بنێرە.")

# بەکارهێنانی infinity_polling بۆ ئەوەی بۆتەکە بەردەوام بێت و نەوەستێت
bot.infinity_polling()
