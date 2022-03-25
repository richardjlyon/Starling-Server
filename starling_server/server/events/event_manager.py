import loguru


class EventManager:
    subscribers = {}

    def subscribe(self, event_name, fn):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(fn)
        loguru.logger.debug("Subscribed to {}".format(event_name))
        loguru.logger.debug(self.subscribers)

    def post_event(self, event_name, event_data):
        loguru.logger.debug("Posting event {}".format(event_name))
        loguru.logger.debug(self.subscribers)
        if event_name not in self.subscribers:
            loguru.logger.warning("No subscribers for event {}".format(event_name))
            return

        for fn in self.subscribers[event_name]:
            loguru.logger.debug("Posting event {} to {}".format(event_name, fn))
            fn(event_data)
