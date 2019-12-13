class CommandDispatcher(object):
    def __init__(self):
        self._handlers_map = {}

    def attach(self, cmd, handler):
        cmd_id = id(cmd)
        if cmd_id not in self._handlers_map:
            self._handlers_map[cmd_id] = list()
        self._handlers_map[cmd_id].append(handler)

    def dispatch(self, command):
        cmd_id = id(type(command))
        if cmd_id in self._handlers_map:
            for h in self._handlers_map[cmd_id]:
                h(command)
