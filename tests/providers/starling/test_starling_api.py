from providers.starling.api import API as StarlingAPI


def test_initialise_token():
    api = StarlingAPI(bank_name="personal")
    assert isinstance(api.token, str)
