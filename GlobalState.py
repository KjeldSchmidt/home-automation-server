from flask import Flask, render_template, redirect

from Controller import Controller


class GlobalState(Controller):
    def __init__(self, app: Flask):
        self.is_turned_on = True
        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route("/global_state/is_turned_on/<bool:state_to_set>")
        def set_turned_on(state_to_set: bool):
            self.turn_on_all() if state_to_set else self.turn_off_all()
            return redirect("/")

    def turn_off_all(self):
        self.is_turned_on = False

    def turn_on_all(self):
        self.is_turned_on = True

    def get_frontend_html(self) -> str:
        return render_template("global_state.html", turned_on=self.is_turned_on)
