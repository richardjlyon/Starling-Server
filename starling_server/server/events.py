"""
Provides methods to subscribe to and publish event_manager.
"""
import loguru

subscribers = {}


def subscribe(event_type: str, fn):
    if event_type not in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(fn)
    loguru.logger.debug("Subscribed to {}".format(event_type))
    loguru.logger.debug(subscribers)


def post_event(event_type: str, data):
    loguru.logger.debug("Posting event {}".format(event_type))
    loguru.logger.debug(subscribers)
    if event_type not in subscribers:
        loguru.logger.warning("No subscribers for event {}".format(event_type))
        return

    for fn in subscribers[event_type]:
        loguru.logger.debug("Posting event {} to {}".format(event_type, fn))
        fn(data)
