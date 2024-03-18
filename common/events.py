class EventHandler:
    def __init__(self):
        self.events = {"all": []}

    def on(self, event_name, callback):
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)
        return self

    def once(self, event_name, callback):
        def wrapper(*args, **kwargs):
            callback(*args, **kwargs)
            self.off(event_name, callback)

        self.on(event_name, wrapper)
        return self

    def off(self, event_name, callback):
        if event_name in self.events:
            self.events[event_name].remove(callback)
        return self

    def emit(self, event_name, *args, **kwargs):
        # print(self.events)
        if event_name in self.events:
            for callback in self.events[event_name]:
                callback(*args, **kwargs)
        for pattern, callbacks in self.events.items():
            if (
                pattern.endswith(".*")
                and event_name.startswith(pattern[:-2])
                or pattern.startswith(("*", "all"))
            ):

                for callback in callbacks:
                    callback(*args, **kwargs)
        return self
