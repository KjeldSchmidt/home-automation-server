from abc import ABC


class Controller(ABC):
    def turn_off_all(self):
        pass

    def turn_on_all(self):
        pass

    def get_frontend_html(self) -> str:
        return ""
