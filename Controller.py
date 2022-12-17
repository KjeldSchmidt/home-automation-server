from abc import ABC


class Controller(ABC):
    def turn_off_all(self):
        pass

    def turn_on_all(self):
        pass

    def produce_main_page_content(self) -> str:
        return ""
