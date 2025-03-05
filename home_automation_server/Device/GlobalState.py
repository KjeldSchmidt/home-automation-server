from flask import Flask, render_template, redirect
from werkzeug import Response

from .Device import Device


class GlobalState(Device):
    def __init__(self, app: Flask) -> None:
        self.is_turned_on = True
        self._setup_routes(app)

    def _setup_routes(self, app: Flask) -> None:
        @app.route("/global_state/is_turned_on/<string:state_to_set>")
        def set_turned_on(state_to_set_raw: str) -> Response:
            # Todo: Introduce a converter, I guess, or find out if there is one... or just switch to FastAPI already.
            if state_to_set_raw == "true":
                state_to_set = True
            elif state_to_set_raw == "false":
                state_to_set = False
            else:
                return Response("Truth value needs to be either 'true' or 'false'", 400)
            self.turn_on_all() if state_to_set else self.turn_off_all()
            return redirect("/")

    def turn_off_all(self) -> None:
        self.is_turned_on = False

    def turn_on_all(self) -> None:
        self.is_turned_on = True

    def get_frontend_html(self) -> str:
        return render_template("global_state.html", turned_on=self.is_turned_on)
