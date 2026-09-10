import os
from dotenv import load_dotenv

# .env file load karo environment variables ke liye
load_dotenv()

# Telegram API Credentials (my.telegram.org se milega)
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

# Owner ID — sirf owner broadcast kar sakta hai
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

# Yuki Music API
MEOW_API_URL = os.environ.get("MEOW_API_URL", "https://music.yukiapi.site")
MEOW_API_KEY = os.environ.get("MEOW_API_KEY", "yuki_28d18045448fe0df857d31dfe08fcdef")

# Directories — downloaded songs store karne ke liye
DOWNLOADS_DIR = "downloads"

# Queue Settings — ek chat me kitne songs queue ho sakte hain
MAX_QUEUE_SIZE = 20

# Bot Info
BOT_NAME = "Cobra"
BOT_VERSION = "1.0.0"

# Default Thumbnail / Media (Video or Image)
DEFAULT_THUMB_URL = os.environ.get(
    "DEFAULT_THUMB_URL",
    "https://graph.org/file/a0d949ae033c97bb60c0b-238eeecbc9c32d092f.mp4"
)
