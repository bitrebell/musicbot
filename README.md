# Telegram Music Bot

A Telegram bot that can play music in group voice chats and download music from YouTube.

## Features
- Play music in group voice chats
- Download music from YouTube
- Queue system for multiple songs
- Basic playback controls (skip, pause, resume)

## Setup
1. Create a new Telegram bot using [@BotFather](https://t.me/botfather)
2. Get your Telegram API credentials (api_id and api_hash) from [my.telegram.org](https://my.telegram.org)
3. Create a `.env` file with your credentials:
```env
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the bot:
```bash
python main.py
```

## Commands
- `/play <song name or URL>` - Play a song from YouTube
- `/skip` - Skip current song
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/stop` - Stop playback and clear queue
- `/queue` - Show current queue 
