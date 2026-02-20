
import requests

client_id = "203271"
client_secret = "a163b230067c0486108c28e956b7bc990ff59ddb"
code = "5d1c15d191156c6a63487c4b2cde0a78f4c98522"

r = requests.post("https://www.strava.com/oauth/token", data={
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code,
    "grant_type": "authorization_code"
})

print(r.json())

#https://www.strava.com/oauth/authorize?client_id=203271&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,activity:read_all
