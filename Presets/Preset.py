class Preset:
    def __init__(
        self, *, ceiling_handlers: dict = None, esp_neopixel_light_handlers: dict = None
    ):
        if ceiling_handlers is None:
            ceiling_handlers = {}
        self.ceiling_handlers = ceiling_handlers

        if esp_neopixel_light_handlers is None:
            esp_neopixel_light_handlers = {}
        self.esp_neopixel_light_handlers = esp_neopixel_light_handlers


Darkness = Preset()
Daylight = Preset(ceiling_handlers={"bedroom": lambda x: x.set_brightness_all(127)})

EveningChillAlone = Preset(
    ceiling_handlers={"bedroom": lambda x: x.set_brightness_all(127)},
    esp_neopixel_light_handlers={
        "bedLamp": lambda x: x.set_mode("CityAtSundown"),
        "beamLamp": lambda x: x.set_mode("CityAtSundown"),
    },
)

EveningChillFriends = Preset(
    ceiling_handlers={"living room": lambda x: x.set_brightness_all(92)},
    esp_neopixel_light_handlers={
        "bedLamp": lambda x: x.set_mode("CityAtSundown"),
        "beamLamp": lambda x: x.set_mode("CityAtSundown"),
    },
)
