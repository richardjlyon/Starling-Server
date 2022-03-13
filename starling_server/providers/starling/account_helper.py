# providers/starling/AccountHelper.py
#
# A helper class to manage Starling API access tokens and default categories.

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import httpx
import toml

from starling_server.config import config_path, tokens_folder
from starling_server.server.schemas.account import AccountSchema


class AccountHelper:
    """
    A helper class to manage account tokens and default_category.

    Accessing the Starling Bank API requires an authentication token, which is stored on the file system in a text file.
    Transactions are allocated a default category which must be specified as part of the API call. This class manages
    storage and retrieval of these items.
    """

    def __init__(self, storage_filepath: Path = None):
        """
        Initialise a helper object.

        Args:
            storage_filepath (pathlib.Path): The filepath of the storage. If None, initialise from filepath in 'config'.
            initialise (bool): If True, rebuild the config file from available tokens
        """

        if storage_filepath is None:
            storage_filepath = config_path.saveFolderPath() / "starling_config.yaml"

        if not storage_filepath.is_file():
            storage_filepath.touch()

        self._storage_filepath = storage_filepath

    @dataclass
    class AccountInfo:
        """A class for passing account information."""

        account_schema: AccountSchema
        token: str
        default_category: uuid.UUID

    async def register_account(self, bank_name: str, account_uuid: uuid.UUID) -> None:
        """
        Register an account in the database.

        Args:
            bank_name (str): The name of the bank (corresponds with the name of the text file storing the access token)
            account_uuid (uuid.UUID): The id of the account to register

        Returns:
            An AccountInfo object with the access token and default category
        """
        # get the token
        token = self._fetch_token(bank_name)

        # get the default category
        (
            default_category,
            account_schema,
        ) = await self._fetch_schema_and_default_category(
            token=token, account_uuid=account_uuid, bank_name=bank_name
        )

        # save the data to the configuration file
        data = {
            "account_schema": account_schema,
            "token": token,
            "default_category": str(default_category),
        }
        config_file = self._load()
        config_file[str(account_uuid)] = data
        self._save(config_file)

    def deregister_account(self, account_uuid: uuid.UUID) -> None:
        """
        Remove an account from the database.

        Args:
            account_uuid (uuid.UUID): The id of the account to remove.
        """
        config_file = self._load()
        if str(account_uuid) in config_file:
            del config_file["str(account_uuid)"]
            self._save(config_file)

    def get_info_for_account_id(self, account_id: uuid.UUID) -> Optional[AccountInfo]:
        """
        Get the account information for the account with the given uuid.

        Args:
            account_id (uuid.UUID): The uuid of the account

        Returns:
            An AccountInfo object with the access token and default category
        """
        config_data = self._load()
        data = config_data.get(str(account_id))

        if data is None:
            return None

        return self.AccountInfo(
            account_schema=AccountSchema(
                uuid=uuid.UUID(data["account_schema"]["uuid"]),
                bank_name=data["account_schema"]["bank_name"],
                account_name=data["account_schema"]["account_name"],
                currency=data["account_schema"]["currency"],
                created_at=data["account_schema"]["created_at"],
            ),
            token=data["token"],
            default_category=data["default_category"],
        )

    @property
    def accounts(self) -> List[AccountInfo]:
        """
        Return the accounts in the configuration file.

        Returns:
            (List[AccountInfo]) The accounts.
        """
        data = self._load()
        return [
            self.AccountInfo(
                account_schema=AccountSchema(
                    uuid=uuid.UUID(data["account_schema"]["uuid"]),
                    bank_name=data["account_schema"]["bank_name"],
                    account_name=data["account_schema"]["account_name"],
                    currency=data["account_schema"]["currency"],
                    created_at=data["account_schema"]["created_at"],
                ),
                token=data["token"],
                default_category=data["default_category"],
            )
            for account_uuid, data in data.items()
        ]

    async def initialise(self) -> int:
        """
        (Re)initialise the config file from tokens in the file system.
        Returns:
            (int) The number of accounts added
        """

        # delete current data from the config file
        with open(self._storage_filepath, "w") as f:
            pass

        bank_names = [
            f.name
            for f in tokens_folder.iterdir()
            if (f.is_file() and f.name != ".DS_Store")
        ]

        count = 0
        for bank_name in bank_names:
            token = self._fetch_token(bank_name)
            accounts = await _get_accounts(token)
            for account in accounts:
                await self.register_account(bank_name, uuid.UUID(account["accountUid"]))
                count += 1

        return count

    def _load(self):
        """Load the data from the file system."""
        with open(self._storage_filepath, "r") as f:
            return toml.load(f)

    def _save(self, config_file: dict):
        """Save the data to the file system."""
        with open(self._storage_filepath, "w") as f:
            toml.dump(config_file, f)

    @staticmethod
    def _fetch_token(bank_name: str) -> str:
        """Fetch the token from the filesystem from the file with name `bank_name`."""
        token_filepath = tokens_folder / bank_name
        try:
            file = open(token_filepath, "r")
        except FileNotFoundError:
            raise FileNotFoundError(f"No token for account type '{bank_name}'")

        return file.read().strip()

    @staticmethod
    async def _fetch_schema_and_default_category(
        token: str, account_uuid: uuid.UUID, bank_name: str
    ) -> (Optional[uuid.UUID], str):
        """Fetch the account schema and default category for the given account uuid."""

        accounts = await _get_accounts(token)

        # NOTE: in testing, using next(etc.) causes "RuntimeError: generator raised StopIteration"
        for account in accounts:
            if account["accountUid"] == str(account_uuid):
                account_schema = {
                    "uuid": str(account_uuid),
                    "bank_name": bank_name,
                    "account_name": account["name"],
                    "currency": account["currency"],
                    "created_at": account["createdAt"],
                }
                default_category = uuid.UUID(account["defaultCategory"])
                return default_category, account_schema


async def _get_accounts(token: str):
    """Get the endpoint from the API with the given authorisation."""
    # FIXME - extract this from StarlingAPI .get() to avoid repetition

    API_BASE_URL = "https://api.starlingbank.com/api/v2"
    url = f"{API_BASE_URL}/accounts"
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "python"}

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
        except httpx.HTTPError as e:
            print(str(e))
            raise Exception(e)

    return r.json()["accounts"]
