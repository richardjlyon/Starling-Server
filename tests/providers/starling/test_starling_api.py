from providers.starling.api import API as StarlingAPI


def test_initialise_token():
    api = StarlingAPI(account_type="personal")
    assert isinstance(api.token, str)
