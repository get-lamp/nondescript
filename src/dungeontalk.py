from core.interp import Interpreter
from core.lang import Lang


class DungeonTalk(Lang):
    def __init__(self, *args, **kwargs):
        super(DungeonTalk, self).__init__(*args, **kwargs)


class DM(Interpreter):
    lang = DungeonTalk()
