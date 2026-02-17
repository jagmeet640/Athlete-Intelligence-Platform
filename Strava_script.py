import os
import time 
import requests
from dotenv import load_dotenv

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_BASE = "https://www.strava.com/api/v3"

class StravaError(Exception):
    pass

def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    pass

def api_get(endpoint: str, access_token: str, params: dict | None = None) -> dict | list:
    pass

def get_athelete(access_token: str) -> dict:
    pass

def get_activities(access_token: str, after_unix: int = 0, per_page: int = 50, max_pages: int = 3) -> list: 
    pass

def main():
    pass


if __name__ == "__main__":
    main()

    