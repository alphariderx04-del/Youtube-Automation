"""
YouTube OAuth authentication.
Pehli baar ye script manually chalani padegi browser ke saath (ek hi baar),
uske baad token.json save ho jaayega aur server pe bina browser ke chalega.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

TOKEN_FILE = "token.pickle"
CLIENT_SECRETS_FILE = "client_secrets.json"


def get_authenticated_service():
    """
    Return an authenticated YouTube API client.
    First run: opens browser for login (run this once on your local machine,
    then copy token.pickle to your server).
    Later runs: uses saved token.pickle silently, no browser needed.
    """
    credentials = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            credentials = pickle.load(f)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"{CLIENT_SECRETS_FILE} nahi mila. Google Cloud Console se "
                    "OAuth client credentials download karke is naam se save karo."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(credentials, f)

    return build("youtube", "v3", credentials=credentials)


if __name__ == "__main__":
    # Run this once locally: python youtube_auth.py
    # Ye token.pickle bana dega, jise server pe copy karna hai
    service = get_authenticated_service()
    print("Authentication successful! token.pickle ban gaya.")
    print("Ab is token.pickle file ko apne cloud server pe is project folder me copy kar do.")
