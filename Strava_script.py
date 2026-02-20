import os
import time 
import requests
from dotenv import load_dotenv

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_BASE = "https://www.strava.com/api/v3"

class StravaError(Exception):
    pass

def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    payload = { 
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    r = requests.post(STRAVA_TOKEN_URL, data = payload, timeout = 30)
    if r.status_code != 200:
        raise StravaError(f"Token refresh failed")
    return r.json()

def api_get(endpoint: str, access_token: str, params: dict | None = None) -> dict | list:
    url = f"{STRAVA_API_BASE}{endpoint}"
    headers = {"Authorization": f"Bearer {access_token}"}

    r = requests.get(url, headers = headers, params = params, timeout=30)

    if r.status_code == 429:
        raise StravaError("rate limited (429). Wait and retry")
    
    if r.status_code != 200:
        raise StravaError(f"GET {endpoint} failed ({r.status_code}) : {r.text}")
    
    return r.json()

def get_athelete(access_token: str) -> dict:
    return api_get("/athlete", access_token)

def get_activities(access_token: str, after_unix: int = 0, per_page: int = 50, max_pages: int = 3) -> list: 
    all_acts = []
    for page in range(1, max_pages + 1): 
        batch = api_get(
            "/athlete/activities",
            access_token,
            params={"after": after_unix, "per_page" : per_page, "page": page},
        )
        if not batch:
            break
        all_acts.extend(batch)
    return all_acts


def main():
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")

    if not client_id or not client_secret or not refresh_token:
        raise SystemExit("Missing STRAVA_CLIENT_ID / STRAVA_CLIENT_SECRET / STRAVA_REFRESH_TOKEN in .env")

    # 1) Refresh token -> access token
    tokens = refresh_access_token(client_id, client_secret, refresh_token)
    access_token = tokens["access_token"]
    expires_at = tokens["expires_at"]
    new_refresh_token = tokens.get("refresh_token")

    print("✅ Access token obtained.")
    print("Expires in (minutes):", max(0, int((expires_at - time.time()) / 60)))

    if new_refresh_token and new_refresh_token != refresh_token:
        print("⚠️ Strava rotated your refresh_token. Update your .env with the new value!")

    # 2) Test connection: /athlete
    athlete = get_athlete(access_token)
    print(f"✅ Connected as: {athlete.get('firstname')} {athlete.get('lastname')} (id={athlete.get('id')})")

    # 3) Fetch some activities (optional)
    # last 30 days
    after_30d = int(time.time() - 30 * 24 * 3600)
    acts = get_activities(access_token, after_unix=after_30d, per_page=50, max_pages=5)
    print(f"✅ Pulled {len(acts)} activities in last 30 days.")
    if acts:
        print("Most recent:", acts[0].get("name"), "|", acts[0].get("start_date"), "|", acts[0].get("type"))


if __name__ == "__main__":
    main()

    