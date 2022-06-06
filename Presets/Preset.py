class Preset:
    def __init__(self, *, ceiling_handlers: dict = None, woodlamp_handlers: dict = None):
        if ceiling_handlers is None:
            ceiling_handlers = {}
        self.ceiling_handlers = ceiling_handlers

        if woodlamp_handlers is None:
            woodlamp_handlers = {}
        self.woodlamp_handlers = woodlamp_handlers


Darkness = Preset()
Daylight = Preset(
    ceiling_handlers={
        "bedroom": lambda x: x.set_brightness_all(127)
    }
)

EveningChillAlone = Preset(
    ceiling_handlers={
        "bedroom": lambda x: x.set_brightness_all(127)
    },
    woodlamp_handlers={
        "bedLamp": lambda x: x.set_mode("CityAtSundown"),
        "beamLamp": lambda x: x.set_mode("CityAtSundown")
    }
)

EveningChillFriends = Preset(
    ceiling_handlers={
        "living room": lambda x: x.set_brightness_all(92)
    },
    woodlamp_handlers={
        "bedLamp": lambda x: x.set_mode("CityAtSundown"),
        "beamLamp": lambda x: x.set_mode("CityAtSundown")
    }
)