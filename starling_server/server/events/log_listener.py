from loguru import logger

from starling_server.server.app import events


def handle_accounts_requested_event(force_refresh: bool = False):
    logger.info(f"Accounts requested, force_refresh={force_refresh}")


def setup_log_listener():
    # subscribe("accounts_requested", handle_accounts_requested_event)
    events.subscribe("accounts_requested", handle_accounts_requested_event)
