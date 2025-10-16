import abc


class GuiElement(abc.ABC):
    @abc.abstractmethod
    def get_frontend_html(self) -> str:
        return ""
