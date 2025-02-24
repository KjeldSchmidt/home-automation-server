from flask import Flask, render_template, redirect

from Controller.Controller import Controller


class GlobalState(Controller):
    def __init__(self, app: Flask):
        self.is_turned_on = True
        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route("/global_state/is_turned_on/<string:state_to_set>")
        def set_turned_on(state_to_set: str):
            # Todo: Introduce a converter, I guess, or find out if there is one... or just switch to FastAPI already.
            if state_to_set == "true":
                state_to_set = True
            elif state_to_set == "false":
                state_to_set = False
            else:
                return "Truth value needs to be either 'true' or 'false'", 400
            self.turn_on_all() if state_to_set else self.turn_off_all()
            return redirect("/")

    def turn_off_all(self):
        self.is_turned_on = False

    def turn_on_all(self):
        self.is_turned_on = True

    def get_frontend_html(self) -> str:
        return render_template("global_state.html", turned_on=self.is_turned_on)
