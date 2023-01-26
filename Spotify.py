import base64
from urllib.parse import urlencode

import requests
from flask import Flask, request, redirect
from Controller import Controller
import env

class Spotify(Controller):
    API_URL = "https://api.spotify.com/api"
    AUTH_URL = 'https://accounts.spotify.com'
    REDIRECT_URI = "http://192.168.178.2:5000/spotify/login/callback"

    def __init__(self, app: Flask):
        self.setup_routes(app)
        self.token: str | None = None

    def setup_routes(self, app: Flask):
        @app.route('/spotify/next')
        def next_song():
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
            }
            response = requests.post('https://api.spotify.com/v1/me/player/next', headers=headers)
            return response.content, response.status_code

        @app.route('/spotify/login')
        def request_user_auth():
            query_params = {
                "client_id": env.SPOTIFY_APP_ID,
                'response_type': 'code',
                'redirect_uri': self.REDIRECT_URI,
                'scope': 'user-modify-playback-state'
            }
            return redirect(f"{self.AUTH_URL}/authorize?{urlencode(query_params)}", code=302)


        @app.route("/spotify/login/callback")
        def trade_auth_code_for_access_token():
            if request.args.get('error'):
                return "You fucked up mate"

            auth_code = request.args.get('code')

            client_auth_raw = f'{env.SPOTIFY_APP_ID}:{env.SPOTIFY_APP_SECRET}'
            client_auth = base64.b64encode(client_auth_raw.encode()).decode()
            headers = {
                'Authorization': f"Basic {client_auth}",
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            payload = "&".join([
                'grant_type=authorization_code',
                f'code={auth_code}',
                f'redirect_uri={self.REDIRECT_URI}'
            ])
            access_code_response = requests.post(
                f"{self.AUTH_URL}/api/token",
                headers=headers,
                data=payload
            )
            self.token = access_code_response.json().get('access_token')
            print(f"Access token retrieve attempt resulted in: {self.token}")

            return f"Access token retrieve attempt resulted in: {self.token}"



