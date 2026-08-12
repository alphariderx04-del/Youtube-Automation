"""
Main automation script.

Kaam: WATCH_FOLDER me nazar rakhta hai. Jab bhi wahan ek naya video
(.mp4/.mov) + uske saath same-naam ka thumbnail (.jpg/.png) milta hai,
to automatically:
  1. OpenAI se title/description/tags generate karta hai
  2. YouTube pe upload karta hai (thumbnail ke saath)
  3. Schedule set karta hai (agar .env me delay diya ho)
  4. Log file me entry daalta hai
  5. Uploaded files ko "done" folder me move kar deta hai

Aapko bas is folder me daalna hai:
  - my_video.mp4
  - my_video.jpg          (thumbnail, same naam)
  - my_video.txt          (optional: video ke baare me chhota note, AI ko madad milegi)
"""

import os
import time
import shutil
import logging
from datetime import datetime
from dotenv import load_dotenv

from content_generator import generate_metadata
from uploader import upload_video

load_dotenv()

WATCH_FOLDER = os.getenv("WATCH_FOLDER", "./videos_to_upload")
DONE_FOLDER = os.path.join(WATCH_FOLDER, "done")
FAILED_FOLDER = os.path.join(WATCH_FOLDER, "failed")
CHECK_INTERVAL_SECONDS = 30

VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi")
THUMBNAIL_EXTENSIONS = (".jpg", ".jpeg", ".png")

os.makedirs(WATCH_FOLDER, exist_ok=True)
os.makedirs(DONE_FOLDER, exist_ok=True)
os.makedirs(FAILED_FOLDER, exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/automation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def find_ready_video_pairs():
    """WATCH_FOLDER me video + matching thumbnail ke pairs dhoondta hai."""
    files = os.listdir(WATCH_FOLDER)
    videos = [f for f in files if f.lower().endswith(VIDEO_EXTENSIONS)]

    pairs = []
    for video in videos:
        base_name = os.path.splitext(video)[0]
        thumbnail = None
        for ext in THUMBNAIL_EXTENSIONS:
            candidate = f"{base_name}{ext}"
            if candidate in files:
                thumbnail = candidate
                break

        if thumbnail:
            note_file = f"{base_name}.txt"
            note_path = os.path.join(WATCH_FOLDER, note_file)
            note_text = ""
            if os.path.exists(note_path):
                with open(note_path, "r", encoding="utf-8") as f:
                    note_text = f.read().strip()

            pairs.append({
                "video": os.path.join(WATCH_FOLDER, video),
                "thumbnail": os.path.join(WATCH_FOLDER, thumbnail),
                "note": note_text,
                "base_name": base_name,
            })
        else:
            logger.info(f"'{video}' mila lekin thumbnail (jpg/png) missing hai — skip kar raha hoon.")

    return pairs


def process_video(pair: dict):
    base_name = pair["base_name"]
    try:
        logger.info(f"Processing: {base_name}")

        logger.info("AI se metadata generate kar raha hoon...")
        metadata = generate_metadata(os.path.basename(pair["video"]), pair["note"])
        logger.info(f"Title generated: {metadata['title']}")

        video_id = upload_video(pair["video"], pair["thumbnail"], metadata)

        logger.info(f"SUCCESS: {base_name} -> https://youtu.be/{video_id}")

        # Move files to done folder
        for path in [pair["video"], pair["thumbnail"]]:
            shutil.move(path, os.path.join(DONE_FOLDER, os.path.basename(path)))

        note_path = os.path.join(WATCH_FOLDER, f"{base_name}.txt")
        if os.path.exists(note_path):
            shutil.move(note_path, os.path.join(DONE_FOLDER, f"{base_name}.txt"))

    except Exception as e:
        logger.error(f"FAILED: {base_name} -> {str(e)}")
        for path in [pair["video"], pair["thumbnail"]]:
            if os.path.exists(path):
                shutil.move(path, os.path.join(FAILED_FOLDER, os.path.basename(path)))


def run_forever():
    logger.info("YouTube automation shuru ho gaya. Watching folder: " + WATCH_FOLDER)
    while True:
        pairs = find_ready_video_pairs()
        if not pairs:
            logger.info("Koi naya video nahi mila. Agla check " + str(CHECK_INTERVAL_SECONDS) + " seconds baad.")
        for pair in pairs:
            process_video(pair)
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_forever()
