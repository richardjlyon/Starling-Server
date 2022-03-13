# AccountHelper.py
#
# A helper class to manage Starling API access tokens and default categories.

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx
import toml

from starling_server.config import config_path, tokens_folder


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
            storage_filepath (): The filepath of the storage. If None, object will be initialised with a system path.
        """

        if storage_filepath is None:
            storage_filepath = config_path.saveFolderPath() / "starling_config.yaml"

        if not storage_filepath.is_file():
            storage_filepath.touch()

        self._filepath = storage_filepath

    @dataclass
    class AccountInfo:
        """A class for passing account information."""

        bank_name: str
        token: str
        default_category: uuid.UUID

    async def register_account(self, bank_name: str, account_uuid: uuid.UUID) -> None:
        """
        Register an account in the database.

        Args:
            bank_name (str): The name of the bank (corresponds with the name of the text file storing the access token)
            default_category (uuid.UUID): The default category associated with this account

        Returns:
            An AccountInfo object with the access token and default category
        """
        # get the token
        token = self._fetch_token(bank_name)

        # get the default category
        default_category = await self._fetch_default_category(
            token=token, account_uuid=account_uuid
        )

        # save the data to the configuration file
        data = {
            "bank_name": bank_name,
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

    def get_for_account_id(self, account_id: uuid.UUID) -> Optional[AccountInfo]:
        """
        Get the account information for the account with the given uuid.

        Args:
            account_id (uuid.UUID): The uuid of the account

        Returns:
            An AccountInfo object with the access token and default category
        """
        config_data = self._load()
        account_data = config_data.get(str(account_id))

        if account_data is None:
            return None

        return self.AccountInfo(
            bank_name=account_data.get("bank_name"),
            token=account_data.get("token"),
            default_category=uuid.UUID(account_data.get("default_category")),
        )

    def _load(self):
        """Load the data from the file system."""
        with open(self._filepath, "r") as f:
            return toml.load(f)

    def _save(self, config_file: dict):
        """Save the data to the file system."""
        with open(self._filepath, "w") as f:
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
    async def _fetch_default_category(
        token: str, account_uuid: uuid.UUID
    ) -> Optional[uuid.UUID]:
        """Fetch the default categgry for the given account uuid."""

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

        accounts = r.json()["accounts"]

        # NOTE: in testing, using next(etc.) causes "RuntimeError: generator raised StopIteration"
        default_category = None
        for account in accounts:
            if account["accountUid"] == str(account_uuid):
                default_category = uuid.UUID(account["defaultCategory"])
                break

        return default_category
