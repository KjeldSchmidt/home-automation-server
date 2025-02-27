import abc

from GuiElement import GuiElement


class Device(GuiElement, abc.ABC):
    @abc.abstractmethod
    def turn_off_all(self):
        pass

    @abc.abstractmethod
    def turn_on_all(self):
        pass
