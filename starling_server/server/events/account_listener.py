from starling_server.server.events import subscribe


def handle_accounts_requested_event(force_refresh: bool = False):
    print("Accounts requested")


def setup_account_listener():
    subscribe("accounts_requested", handle_accounts_requested_event)
