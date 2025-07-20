import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp
from collections import deque
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize Pyrogram client
app = Client(
    "music_bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

# Initialize PyTgCalls client
call_py = PyTgCalls(app)

# Queue to store songs
queue = {}  # chat_id: deque([(title, file_path), ...])
current_song = {}  # chat_id: (title, file_path)

# Create downloads directory if it doesn't exist
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# YouTube-DL options
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

async def download_audio(url):
    """Download audio from YouTube URL"""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            title = info['title']
            file_path = str(DOWNLOAD_DIR / f"{title}.mp3")
            return title, file_path
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None, None

async def play_next(chat_id):
    """Play next song in queue"""
    if chat_id not in queue or not queue[chat_id]:
        current_song[chat_id] = None
        return

    title, file_path = queue[chat_id].popleft()
    current_song[chat_id] = (title, file_path)
    
    try:
        await call_py.join_group_call(
            chat_id,
            AudioPiped(file_path)
        )
    except Exception as e:
        print(f"Error playing audio: {e}")
        await play_next(chat_id)

@app.on_message(filters.command("play"))
async def play_cmd(client, message):
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        await message.reply_text("Please provide a song name or YouTube URL!")
        return

    query = " ".join(message.command[1:])
    
    # Initialize queue for this chat if it doesn't exist
    if chat_id not in queue:
        queue[chat_id] = deque()

    # Download the song
    await message.reply_text(f"⏳ Downloading: {query}")
    title, file_path = await download_audio(query)
    
    if not title or not file_path:
        await message.reply_text("❌ Failed to download the song!")
        return

    # Add to queue
    queue[chat_id].append((title, file_path))
    await message.reply_text(f"✅ Added to queue: {title}")

    # If no song is playing, start playing
    if chat_id not in current_song or not current_song[chat_id]:
        await play_next(chat_id)

@app.on_message(filters.command("skip"))
async def skip_cmd(client, message):
    chat_id = message.chat.id
    if chat_id in current_song and current_song[chat_id]:
        await call_py.leave_group_call(chat_id)
        await play_next(chat_id)
        await message.reply_text("⏭ Skipped to next song")
    else:
        await message.reply_text("❌ No song is currently playing!")

@app.on_message(filters.command("stop"))
async def stop_cmd(client, message):
    chat_id = message.chat.id
    if chat_id in queue:
        queue[chat_id].clear()
    if chat_id in current_song:
        current_song[chat_id] = None
    await call_py.leave_group_call(chat_id)
    await message.reply_text("⏹ Stopped playing and cleared queue")

@app.on_message(filters.command("queue"))
async def queue_cmd(client, message):
    chat_id = message.chat.id
    if chat_id not in queue or not queue[chat_id]:
        await message.reply_text("Queue is empty!")
        return

    queue_list = "🎵 Current Queue:\n"
    for i, (title, _) in enumerate(queue[chat_id], 1):
        queue_list += f"{i}. {title}\n"
    
    if chat_id in current_song and current_song[chat_id]:
        current_title = current_song[chat_id][0]
        queue_list = f"🎵 Now Playing: {current_title}\n\n" + queue_list

    await message.reply_text(queue_list)

@app.on_message(filters.command("pause"))
async def pause_cmd(client, message):
    chat_id = message.chat.id
    try:
        await call_py.pause_stream(chat_id)
        await message.reply_text("⏸ Paused")
    except:
        await message.reply_text("❌ Nothing is playing!")

@app.on_message(filters.command("resume"))
async def resume_cmd(client, message):
    chat_id = message.chat.id
    try:
        await call_py.resume_stream(chat_id)
        await message.reply_text("▶️ Resumed")
    except:
        await message.reply_text("❌ Nothing is paused!")

# Start the bot
async def main():
    await call_py.start()
    await app.start()
    print("Bot started!")
    await PyTgCalls.idle()

if __name__ == "__main__":
    asyncio.run(main()) 