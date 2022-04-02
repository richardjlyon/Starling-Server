"""
An Account is a helper class to simplify access to the provider.
"""

import importlib
import os
from dataclasses import dataclass, field
from typing import Type

from starling_server import cfg
from starling_server.providers.provider import Provider
from starling_server.server.schemas import AccountSchema


@dataclass
class BankInfo:
    """Handles information for a bank in the config file."""

    bank_name: str
    class_name: str
    library_name: str
    token_name: str


@dataclass
class Account:
    """Represents the schema and provider for an account."""

    schema: AccountSchema
    provider: Provider = field(init=False)

    def __post_init__(self):
        """Initialise the provider."""
        provider_class = get_provider_class(self.schema.bank_name)
        auth_token = get_auth_token(self.schema.bank_name)
        self.provider = provider_class(
            auth_token=auth_token,
            bank_name=self.schema.bank_name,
            account_uuid=self.schema.uuid,
        )


def get_provider_class(bank_name: str) -> Type[Provider]:
    """Returns a provider class computed from provider_name."""
    bank_info = get_bank_info(bank_name)
    module = importlib.import_module(
        f"starling_server.providers.{bank_info.library_name}.api"
    )
    return getattr(module, bank_info.class_name)


def get_auth_token(bank_name: str) -> str:
    """Returns the auth token for the given bank."""
    bank_info = get_bank_info(bank_name)
    return os.environ[bank_info.token_name]


def get_bank_info(bank_name: str) -> BankInfo:
    """Returns a bank info object computed from bank_name, or RuntimeError."""
    banks = [BankInfo(**bank) for bank in cfg.banks]
    for bank in banks:
        if bank.bank_name == bank_name:
            return bank

    raise RuntimeError(f"No bank info found for bank '{bank_name}'")
