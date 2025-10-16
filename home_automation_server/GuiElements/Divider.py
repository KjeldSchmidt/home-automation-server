from GuiElement import GuiElement


class DividerSingleton(GuiElement):
    def __init__(self):
        raise RuntimeError("Instead of instantiating this class, use the provided `Divider` instance.")

    def get_frontend_html(self) -> str:
        return "<hr />"


Divider = DividerSingleton.__new__(DividerSingleton)
