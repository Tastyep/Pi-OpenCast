import configparser


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Server(object):
    host = '0.0.0.0'
    port = 2020


class VideoPlayer(object):
    hide_background = True
    loop_last = True
    history_size = 15


class Downloader(object):
    output_directory = '/tmp'


class Subtitle(object):
    language = 'eng'


class Config(object):
    __metaclass__ = Singleton

    def __init__(self):
        self._parser = configparser.ConfigParser()
        self._init_cache()

    def __getitem__(self, key):
        return self._entries.get(key)

    def load_from_file(self, path):
        with open(path, 'r') as file:
            self._parser.read_file(file)
            self._load_cache()

    def load_from_dict(self, dict):
        self._parser.read_dict(dict)
        self._load_cache()

    def _init_cache(self):
        self._entries = {
            'Server': Server(),
            'VideoPlayer': VideoPlayer(),
            'Downloader': Downloader(),
            'Subtitle': Subtitle()
        }

    def _load_cache(self):
        for key, category in self._entries.items():
            if not self._parser.has_section(key):
                continue
            parser = self._parser[key]

            for entry_name in dir(category):
                if (entry_name.startswith('__')
                        or not self._parser.has_option(key, entry_name)):
                    continue
                self._parse_entry(parser, category, entry_name)

    def _parse_entry(self, parser, category, entry_name):
        entry = getattr(category, entry_name)
        value = entry

        if type(entry) is int:
            value = parser.getint(entry_name, fallback=entry)
        elif type(entry) is float:
            value = parser.getfloat(entry_name, fallback=entry)
        elif type(entry) is bool:
            value = parser.getboolean(entry_name, fallback=entry)
        else:
            value = parser.get(entry_name, fallback=entry)
            if (type(entry) is str and (value.startswith(
                ("'", '"')) and value[0] is value[-1])):
                value = value[1:-1]
        setattr(category, entry_name, value)


config = Config()
