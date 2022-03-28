import importlib
import os
import uuid

from starling_server import cfg
from starling_server.providers.provider import Provider
from starling_server.server.schemas import AccountSchema


def get_provider_class(bank_name: str, account_uuid: uuid.UUID) -> Provider:
    """Returns a provider class computed from provider_name"""

    library_name = cfg[bank_name].library_name
    class_name = cfg[bank_name].class_name
    token_name = cfg[bank_name].token_name

    module = importlib.import_module(f"starling_server.providers.{library_name}.api")
    class_ = getattr(module, class_name)
    auth_token = os.environ[token_name]

    return class_(auth_token=auth_token, bank_name=bank_name, account_uuid=account_uuid)


class Account:
    """Provides the schema and provider for an account."""

    def __init__(self, schema: AccountSchema):
        self.schema: AccountSchema = schema
        self.provider = get_provider_class(schema.bank_name, schema.uuid)
