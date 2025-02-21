from flask import Flask, render_template, redirect

from Controller import Controller


class GlobalState(Controller):
    def __init__(self, app: Flask):
        self.turned_on = True
        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route("/global/turned_on/true")
        def turn_on_global():
            self.turned_on = True
            return redirect("/")

        @app.route("/global/turned_on/false")
        def turn_off_global():
            self.turned_on = False
            return redirect("/")

    def turn_off_all(self):
        self.turned_on = False

    def turn_on_all(self):
        self.turned_on = True

    def get_frontend_html(self) -> str:
        return render_template("global_state.html", turned_on=self.turned_on)
