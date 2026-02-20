# import os
# import time
# import requests
# from dotenv import load_dotenv

# load_dotenv(".env")

# STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
# STRAVA_API_BASE = "https://www.strava.com/api/v3"


# class StravaError(Exception):
#     pass


# def must_env(name: str) -> str:
#     v = os.getenv(name)
#     if not v:
#         raise StravaError(f"Missing {name} in .env")
#     return v.strip()


# def token_exchange_authorization_code(client_id: str, client_secret: str, code: str) -> dict:
#     """
#     One-time exchange: authorization code -> access_token + refresh_token
#     """
#     data = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "code": code,
#         "grant_type": "authorization_code",
#     }
#     r = requests.post(STRAVA_TOKEN_URL, data=data, timeout=30)
#     if r.status_code != 200:
#         raise StravaError(f"Auth-code exchange failed ({r.status_code}): {r.text}")
#     return r.json()


# def token_refresh(client_id: str, client_secret: str, refresh_token: str) -> dict:
#     """
#     Ongoing refresh: refresh_token -> new access_token
#     """
#     data = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "grant_type": "refresh_token",
#         "refresh_token": refresh_token,
#     }
#     r = requests.post(STRAVA_TOKEN_URL, data=data, timeout=30)
#     if r.status_code != 200:
#         raise StravaError(f"Refresh failed ({r.status_code}): {r.text}")
#     return r.json()


# def api_get(endpoint: str, access_token: str, params: dict | None = None):
#     url = f"{STRAVA_API_BASE}{endpoint}"
#     headers = {"Authorization": f"Bearer {access_token}"}

#     r = requests.get(url, headers=headers, params=params, timeout=30)

#     if r.status_code == 429:
#         raise StravaError(f"Rate limited (429): {r.text}")

#     if r.status_code == 401:
#         # show real reason from Strava
#         raise StravaError(f"Unauthorized (401) on {endpoint}: {r.text}")

#     if r.status_code != 200:
#         raise StravaError(f"GET {endpoint} failed ({r.status_code}): {r.text}")

#     return r.json()


# def get_athlete(access_token: str):
#     return api_get("/athlete", access_token)


# def get_activities(access_token: str, after_unix: int, per_page: int = 50, max_pages: int = 5):
#     all_acts = []
#     for page in range(1, max_pages + 1):
#         batch = api_get(
#             "/athlete/activities",
#             access_token,
#             params={"after": after_unix, "per_page": per_page, "page": page},
#         )
#         if not batch:
#             break
#         all_acts.extend(batch)
#     return all_acts


# def main():
#     client_id = must_env("STRAVA_CLIENT_ID")
#     client_secret = must_env("STRAVA_CLIENT_SECRET")

#     # Optional: one-time auth code exchange
#     auth_code = (os.getenv("STRAVA_AUTH_CODE") or "").strip()
#     refresh_token = (os.getenv("STRAVA_REFRESH_TOKEN") or "").strip()

#     if auth_code:
#         print("🔁 Exchanging AUTH CODE for tokens (one-time)...")
#         tokens = token_exchange_authorization_code(client_id, client_secret, auth_code)
#         print("✅ Exchange success.")
#         print("IMPORTANT: Save this refresh_token in your .env and then remove STRAVA_AUTH_CODE.")
#         print("refresh_token (first 8 chars):", tokens.get("refresh_token", "")[:8])
#         # Print scope if Strava includes it
#         if "scope" in tokens:
#             print("scope:", tokens["scope"])
#         else:
#             print("scope: (not returned by Strava in this response)")
#         return

#     if not refresh_token:
#         raise StravaError("No STRAVA_REFRESH_TOKEN set. Either set STRAVA_AUTH_CODE once or add refresh token to .env")

#     print("🔐 Refreshing access token...")
#     tokens = token_refresh(client_id, client_secret, refresh_token)

#     access_token = tokens.get("access_token")
#     expires_at = tokens.get("expires_at")
#     new_refresh = tokens.get("refresh_token")

#     if not access_token:
#         raise StravaError(f"Refresh response missing access_token: {tokens}")

#     print("✅ Access token obtained.")
#     if expires_at:
#         print("Expires in (minutes):", max(0, int((int(expires_at) - time.time()) / 60)))

#     if new_refresh and new_refresh != refresh_token:
#         print("⚠️ Strava rotated your refresh token. Update .env with the NEW one!")
#         print("new refresh_token (first 8 chars):", new_refresh[:8])

#     if "scope" in tokens:
#         print("scope:", tokens["scope"])

#     print("\n👤 Testing /athlete ...")
#     athlete = get_athlete(access_token)
#     print(f"✅ Connected as: {athlete.get('firstname')} {athlete.get('lastname')} (id={athlete.get('id')})")

#     print("\n📊 Fetching last 30 days activities ...")
#     after_30d = int(time.time() - 30 * 24 * 3600)
#     acts = get_activities(access_token, after_unix=after_30d, per_page=50, max_pages=5)

#     print(f"✅ Pulled {len(acts)} activities in last 30 days.")
#     if acts:
#         a0 = acts[0]
#         print("Most recent:", a0.get("name"), "|", a0.get("start_date"), "|", a0.get("type"))


# if __name__ == "__main__":
#     main()



from stravalib import Client
import webbrowser
import os
from dotenv import load_dotenv

# Load environment variables (optional, but recommended)
load_dotenv()
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REDIRECT_URL = "http://127.0.0.1:5000/authorization" # Must match your app settings

client = Client()

# 1. Generate the authorization URL and open it in a browser
url = client.authorization_url(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URL,
    scope=['read_all', 'activity:read_all'] # Requesting broad read access
)
print(f"Go to this URL to authorize: {url}")
webbrowser.open(url)

# 2. After authorization, Strava redirects to your URL (which will show a 'page not found' error).
# Copy the 'code' value from the URL in your browser (e.g., in http://localhost/?code=YOUR_CODE_HERE&...)
code = input("Please enter the code from the URL: ")

# 3. Exchange the code for a token set
token_response = client.exchange_code_for_token(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    code=code
)

# Save these tokens for future use (e.g., in a JSON file)
import json
with open('strava_tokens.json', 'w') as f:
    json.dump(token_response, f, indent=4)

print("Tokens saved to strava_tokens.json")
