
import configparser


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(object):
    __metaclass__ = Singleton

    def __init__(self):
        self._parser = configparser.RawConfigParser()
        self._init_cache()

    def load(self, path):
        with open(path, 'r') as file:
            self._parser.read_file(file)
            self._load_cache()

    @property
    def hide_background(self):
        return self._hide_background

    def _init_cache(self):
        self._hide_background = False

    def _load_cache(self):
        player = self._parser['Player']
        self._hide_background = player.getboolean(
            'hide_background', fallback=self._hide_background)


config = Config()
