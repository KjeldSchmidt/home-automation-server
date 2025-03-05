class Preset:
    def __init__(self, *, zigbee_light_handlers: dict | None = None, esp_neopixel_light_handlers: dict | None = None):
        if zigbee_light_handlers is None:
            zigbee_light_handlers = {}
        self.zigbee_light_handlers = zigbee_light_handlers

        if esp_neopixel_light_handlers is None:
            esp_neopixel_light_handlers = {}
        self.esp_neopixel_light_handlers = esp_neopixel_light_handlers


Darkness = Preset()
Daylight = Preset(zigbee_light_handlers={"bedroom": lambda x: x.set_brightness_all(127)})

EveningChillAlone = Preset(
    zigbee_light_handlers={"bedroom": lambda x: x.set_brightness_all(127)},
    esp_neopixel_light_handlers={
        "bedLamp": lambda x: x.set_mode("CityAtSundown"),
        "beamLamp": lambda x: x.set_mode("CityAtSundown"),
    },
)

EveningChillFriends = Preset(
    zigbee_light_handlers={"living room": lambda x: x.set_brightness_all(92)},
    esp_neopixel_light_handlers={
        "bedLamp": lambda x: x.set_mode("CityAtSundown"),
        "beamLamp": lambda x: x.set_mode("CityAtSundown"),
    },
)
