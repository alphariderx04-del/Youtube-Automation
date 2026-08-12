"""
YouTube pe video + thumbnail + metadata upload karta hai, aur schedule bhi set karta hai.
"""

import os
import datetime
from googleapiclient.http import MediaFileUpload

from youtube_auth import get_authenticated_service


def upload_video(video_path: str, thumbnail_path: str, metadata: dict) -> str:
    """
    video_path: local path of the video file
    thumbnail_path: local path of the thumbnail image (manual banaya hua)
    metadata: dict with title, description, tags (list)

    Returns: uploaded video ID
    """
    youtube = get_authenticated_service()

    privacy_status = os.getenv("DEFAULT_PRIVACY_STATUS", "private")
    category_id = os.getenv("DEFAULT_CATEGORY_ID", "22")
    delay_minutes = int(os.getenv("SCHEDULE_DELAY_MINUTES", "0"))

    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("tags", []),
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    # Agar schedule karna hai to publishAt set karo (privacyStatus must be "private" for scheduling)
    if delay_minutes > 0:
        publish_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=delay_minutes)
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_time.isoformat("T") + "Z"

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"Uploading: {video_path} ...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"Upload complete. Video ID: {video_id}")

    # Thumbnail set karo
    if thumbnail_path and os.path.exists(thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path),
        ).execute()
        print("Thumbnail set ho gaya.")

    return video_id
