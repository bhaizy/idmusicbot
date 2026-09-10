# Raiway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?code=907kP9&referralCode=C3Eb1N)

# 🐍 Cobra — Telegram ID Music Userbot

Aapki **apni Telegram ID** se chalega ek powerful **Music Userbot**. Voice chat mein music play karega. Link ya song name do — gaana bajega!

![Cobra Thumbnail](https://graph.org/file/a0d949ae033c97bb60c0b-238eeecbc9c32d092f.mp4)

---

## ✨ Features

- 🐍 **Userbot Mode** — Aapki personal ID se voice chat join karta hai
- 🎵 **Yuki Music API** — Superfast audio & video stream download
- 🎬 **Video Stream** — VC mein HD video stream support (`.vplay`)
- 📁 **Direct Audio Reply** — Kisi bhi audio/voice message pe reply karke `.play` karo
- 📋 **Queue System** — Unlimited songs queue support
- 📥 **Chat Downloader** — Direct audio (`.song`) aur video (`.vsong`) download chat mein
- 📝 **Lyrics Finder** — Instant lyrics search (`.lyrics`)
- 📢 **Broadcast** — Sabhi saved users aur groups ko ek click me message bhejo
- 📊 **Live Stats & Ping** — Bot uptime, system stats, ping response
- ☁️ **Cloud Ready** — Railway & Heroku 1-click deploy support

---

## 📋 Commands List

### 🎶 Voice Chat Player
| Command | Description |
|---------|-------------|
| `.play <query/link>` | 🎵 Voice chat mein audio stream play karega |
| `.play` *(reply to audio)* | 📁 Kisi bhi audio/voice message ko direct VC mein play karega |
| `.vplay <query/link>` | 🎬 Voice chat mein video stream play karega |
| `.skip` | ⏭️ Current gaana skip karke agla play karega |
| `.stop` | ⏹️ Playback stop karke voice chat chhod dega |
| `.pause` | ⏸️ Stream ko pause karega |
| `.resume` | ▶️ Paused stream ko wapas resume karega |
| `.queue` | 📋 Up next queue list dikhayega |
| `.np` | 🎧 Abhi baj raha gaana (Now Playing) info |

### 📥 Direct Downloader & Tools
| Command | Description |
|---------|-------------|
| `.song <name/link>` | 🎵 Audio MP3 file download karke chat mein send karega |
| `.vsong <name/link>` | 🎬 Video file download karke chat mein send karega |
| `.lyrics <song>` | 📝 Gaane ke lyrics find karke layega |
| `.ping` | 🏓 Bot response time aur status check karega |
| `.stats` | 📊 Users, groups, played songs, CPU/RAM stats dikhayega |
| `.clean` | 🧹 Downloads folder saaf karega *(Owner Only)* |
| `.broadcast <msg>` | 📢 Sabhi users/groups ko broadcast message karega *(Owner Only)* |
| `.help` | ❓ Sabhi commands ka menu dikhayega |

---

## 🛠 Requirements

- Python 3.10+
- FFmpeg installed
- Telegram API Credentials (`API_ID` & `API_HASH`)
- Pyrogram String Session

---

## 🚀 Setup & Installation

### Step 1: Telegram API Credentials
1. [my.telegram.org](https://my.telegram.org) pe jaao aur login karo.
2. **API Development Tools** pe click karo.
3. App details bharkar `API_ID` aur `API_HASH` generate karo.

### Step 2: Pyrogram String Session
String session generate karne ke liye ye command chalaao:
```python
from pyrogram import Client

api_id = int(input("API_ID: "))
api_hash = input("API_HASH: ")

with Client("session_gen", api_id=api_id, api_hash=api_hash) as app:
    print(f"\nYour STRING_SESSION:\n{app.export_session_string()}")
```

### Step 3: Configure Environment
`.env.example` ko copy karke `.env` banao:
```bash
cp .env.example .env
```

`.env` file mein apni details daalo:
```env
API_ID=12345
API_HASH=your_api_hash_here
STRING_SESSION=your_pyrogram_string_session_here
OWNER_ID=your_telegram_user_id
MEOW_API_URL=https://music.yukiapi.site
MEOW_API_KEY=yuki_28d18045448fe0df857d31dfe08fcdef
DEFAULT_THUMB_URL=https://graph.org/file/a0d949ae033c97bb60c0b-238eeecbc9c32d092f.mp4
```

### Step 4: Run Locally
```bash
# Requirements install karo
pip install -r requirements.txt

# FFmpeg install karo (Debian/Ubuntu)
sudo apt update && sudo apt install ffmpeg -y

# Bot run karo
python main.py
```

---

## ☁️ Deploy on Railway

1. GitHub pe code push karo.
2. [Railway.app](https://railway.app) pe jaao aur **New Project** -> **Deploy from GitHub repo** select karo.
3. Variables tab mein `.env` ke saare variables daalo.
4. `railway.toml` pehle se configured hai, build & deploy automatically ho jaayega! 🚀

---

## ☁️ Deploy on Heroku

1. [Heroku](https://heroku.com) dashboard pe jaakar New App banao.
2. Settings tab mein **Config Vars** set karo (`API_ID`, `API_HASH`, `STRING_SESSION`, etc.).
3. **Buildpacks** add karo:
   - `heroku/python`
   - `https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest`
4. App deploy hone ke baad **Resources** tab mein `worker` dyno ko **ON** karo.

---

## 📁 Project Structure

```
idmusicbot/
├── config.py              # Configuration & Environment loader
├── main.py                # Bot startup & PyTgCalls client
├── plugins/
│   ├── __init__.py
│   ├── play.py            # .play, .vplay, reply to audio
│   ├── controls.py        # .skip, .stop, .pause, .resume
│   ├── queue_cmd.py       # .queue, .np
│   ├── broadcast.py       # .broadcast (Owner only)
│   ├── stats.py           # .stats
│   └── extra.py           # .song, .vsong, .lyrics, .ping, .clean, .help
├── utils/
│   ├── __init__.py
│   ├── db.py              # TinyDB storage for broadcast & stats
│   ├── queue_manager.py   # Song queue per chat
│   ├── stream.py          # PyTgCalls voice chat stream manager
│   └── youtube.py         # YouTube search & Yuki API downloader
├── requirements.txt       # Dependencies
├── Procfile               # Heroku process definition
├── railway.toml           # Railway nixpacks config
├── runtime.txt            # Python 3.11.9
└── README.md
```

---

**🐍 Cobra ID Music Bot — Fast, Lightweight & Powerful!**
