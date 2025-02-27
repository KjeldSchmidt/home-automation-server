import base64
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from flask import Flask, request, redirect, render_template
from Device.Device import Device
from home_automation_server import env


@dataclass
class AuthorisationResponse:
    access_token: str | None
    expires_in: int | None
    status_code: int
    response_body: str
    expiry_datetime: datetime = field(init=False)

    def __post_init__(self):
        now = datetime.now()
        self.expiry_datetime = now + timedelta(seconds=self.expires_in - 60)


class Spotify(Device):
    API_URL = "https://api.spotify.com/api"
    AUTH_URL = "https://accounts.spotify.com"
    REDIRECT_URI = "http://192.168.178.2:5000/spotify/login/callback"

    def __init__(self, app: Flask):
        refresh_response = self.refresh_access_token()
        self.token: str = refresh_response.access_token
        self.token_expiry: datetime = refresh_response.expiry_datetime
        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route("/spotify/next")
        def next_song():
            self.ensure_token_is_fresh()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post("https://api.spotify.com/v1/me/player/next", headers=headers)
            return response.content, response.status_code

        @app.route("/spotify/previous")
        def previous_song():
            self.ensure_token_is_fresh()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post("https://api.spotify.com/v1/me/player/previous", headers=headers)
            return response.content, response.status_code

        @app.route("/spotify/play-pause")
        def play_pause():
            self.ensure_token_is_fresh()
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            requests.put(
                "https://api.spotify.com/v1/me/player/shuffle?state=true",
                headers=headers,
            )
            response = requests.put(
                "https://api.spotify.com/v1/me/player/play",
                headers=headers,
                json={"context_uri": "spotify:playlist:3PhrgXmaPgAqKuYCNP8QrH"},
            )
            return response.content, response.status_code

        @app.route("/spotify/play/<string:category_id>/<string:spotify_id>")
        def play_thing(category_id: str, spotify_id: str):
            self.ensure_token_is_fresh()
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            requests.put(
                "https://api.spotify.com/v1/me/player/shuffle?state=false",
                headers=headers,
            )
            response = requests.put(
                "https://api.spotify.com/v1/me/player/play",
                headers=headers,
                json={"context_uri": f"spotify:{category_id}:{spotify_id}"},
            )
            return response.content, response.status_code

        @app.route("/spotify/login")
        def request_user_auth():
            query_params = {
                "client_id": env.SPOTIFY_APP_ID,
                "response_type": "code",
                "redirect_uri": self.REDIRECT_URI,
                "scope": "user-modify-playback-state",
            }
            return redirect(f"{self.AUTH_URL}/authorize?{urlencode(query_params)}", code=302)

        @app.route("/spotify/login/callback")
        def trade_auth_code_for_access_token():
            if request.args.get("error"):
                return "You fucked up mate"

            auth_code = request.args.get("code")

            client_auth_raw = f"{env.SPOTIFY_APP_ID}:{env.SPOTIFY_APP_SECRET}"
            client_auth = base64.b64encode(client_auth_raw.encode()).decode()
            headers = {
                "Authorization": f"Basic {client_auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            payload = "&".join(
                [
                    "grant_type=authorization_code",
                    f"code={auth_code}",
                    f"redirect_uri={self.REDIRECT_URI}",
                ]
            )
            access_code_response = requests.post(f"{self.AUTH_URL}/api/token", headers=headers, data=payload)
            self.token = access_code_response.json().get("access_token")
            result_message = f"Access token retrieve attempt resulted in: {access_code_response.json()}"
            print(result_message)

            return result_message

        @app.route("/spotify/login/refresh")
        def refresh_access_token() -> tuple[str, int]:
            refresh_result = self.refresh_access_token()
            return refresh_result.response_body, refresh_result.status_code

    def ensure_token_is_fresh(self):
        if datetime.now() > self.token_expiry:
            refresh_response = self.refresh_access_token()
            self.token = refresh_response.access_token
            self.token_expiry = refresh_response.expiry_datetime

    def refresh_access_token(self) -> AuthorisationResponse:
        client_auth_raw = f"{env.SPOTIFY_APP_ID}:{env.SPOTIFY_APP_SECRET}"
        client_auth = base64.b64encode(client_auth_raw.encode()).decode()
        headers = {
            "Authorization": f"Basic {client_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        payload = "&".join(
            [
                "grant_type=refresh_token",
                f"refresh_token={env.SPOTIFY_REFRESH_TOKEN}",
                f"client_id={env.SPOTIFY_APP_ID}",
            ]
        )
        refresh_response = requests.post(f"{self.AUTH_URL}/api/token", headers=headers, data=payload)

        result_message = f"Access token refresh attempt resulted in: {refresh_response.json()}"
        print(result_message)

        token = refresh_response.json().get("access_token")
        expires_in = refresh_response.json().get("expires_in")
        response = AuthorisationResponse(
            access_token=token,
            expires_in=expires_in,
            status_code=refresh_response.status_code,
            response_body=refresh_response.text,
        )
        return response

    def get_frontend_html(self) -> str:
        return render_template("spotify.html")

    def turn_on_all(self):
        raise NotImplementedError()

    def turn_off_all(self):
        raise NotImplementedError()
