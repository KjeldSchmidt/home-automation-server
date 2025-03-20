import base64
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from flask import Flask, request, redirect, render_template
from werkzeug import Response

from .Device import Device


@dataclass
class AuthorisationResponse:
    access_token: str | None
    expires_in: int | None
    status_code: int
    response_body: str
    expiry_datetime: datetime = field(init=False)

    def __post_init__(self) -> None:
        expires_in = self.expires_in
        if expires_in is None:
            expires_in = 29 * 60  # Assume token expires in 30 minutes, add some buffer

        now = datetime.now()
        self.expiry_datetime = now + timedelta(seconds=expires_in - 60)


class Spotify(Device):
    API_URL = "https://api.spotify.com/api"
    AUTH_URL = "https://accounts.spotify.com"
    REDIRECT_URI = "http://192.168.178.2:5000/spotify/login/callback"

    def __init__(self, app: Flask, app_id: str, app_secret: str, refresh_token: str):
        refresh_response = self.refresh_access_token()
        self.token: str | None = refresh_response.access_token
        self.token_expiry = refresh_response.expiry_datetime
        self._setup_routes(app)
        self.app_id = app_id
        self.app_secret = app_secret
        self.refresh_token = refresh_token

    def _setup_routes(self, app: Flask) -> None:
        @app.route("/spotify/next")
        def next_song() -> Response:
            self.ensure_token_is_fresh()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post("https://api.spotify.com/v1/me/player/next", headers=headers)
            return Response(response.content, response.status_code)

        @app.route("/spotify/previous")
        def previous_song() -> Response:
            self.ensure_token_is_fresh()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post("https://api.spotify.com/v1/me/player/previous", headers=headers)
            return Response(response.content, response.status_code)

        @app.route("/spotify/play-pause")
        def play_pause() -> Response:
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
            return Response(response.content, response.status_code)

        @app.route("/spotify/play/<string:category_id>/<string:spotify_id>")
        def play_thing(category_id: str, spotify_id: str) -> Response:
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
            return Response(response.content, response.status_code)

        @app.route("/spotify/login")
        def request_user_auth() -> Response:
            query_params = {
                "client_id": self.app_id,
                "response_type": "code",
                "redirect_uri": self.REDIRECT_URI,
                "scope": "user-modify-playback-state",
            }
            return redirect(f"{self.AUTH_URL}/authorize?{urlencode(query_params)}", code=302)

        @app.route("/spotify/login/callback")
        def trade_auth_code_for_access_token() -> str:
            if request.args.get("error"):
                return "You fucked up mate"

            auth_code = request.args.get("code")

            client_auth_raw = f"{self.app_id}:{self.app_secret}"
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

    def ensure_token_is_fresh(self) -> None:
        if datetime.now() > self.token_expiry:
            refresh_response = self.refresh_access_token()
            self.token = refresh_response.access_token
            self.token_expiry = refresh_response.expiry_datetime

    def refresh_access_token(self) -> AuthorisationResponse:
        client_auth_raw = f"{self.app_id}:{self.app_secret}"
        client_auth = base64.b64encode(client_auth_raw.encode()).decode()
        headers = {
            "Authorization": f"Basic {client_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        payload = "&".join(
            [
                "grant_type=refresh_token",
                f"refresh_token={self.refresh_token}",
                f"client_id={self.app_id}",
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

    def turn_on_all(self) -> None:
        raise NotImplementedError()

    def turn_off_all(self) -> None:
        raise NotImplementedError()
