class ControllerCollection:
    def __init__(self, controllers: list):
        self.controllers = controllers

    def produce_main_page_content(self):
        return "<hr />".join(
            [controller.produce_main_page_content() for controller in self.controllers]
        )

    def turn_off_all(self):
        for controller in self.controllers:
            controller.turn_off_all()

    def turn_on_all(self):
        for controller in self.controllers:
            controller.turn_on_all()
