import asyncio
import os
from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.bcs import Serializer
from aptos_sdk.account_address import AccountAddress  # Import this
from aptos_sdk.type_tag import TypeTag, StructTag
import requests
from dotenv import load_dotenv
from typing import Any, List

load_dotenv()


class AptosTransactionHandler:

    def __init__(self, rest_client: RestClient, account: Account):
        self.rest_client = rest_client
        self.account = account

    def fetch_payload(self, api_url, params, headers):
        try:
            response = requests.get(api_url, params=params, headers=headers)
            response.raise_for_status()
            return response.json().get("data")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching payload: {e}")
            return None

    def create_transaction_function_arguments(
        self, arguments: List[Any], types: List[Serializer]
    ) -> List[TransactionArgument]:
        if len(arguments) != len(types):
            raise ValueError("Arguments and types length mismatch.")

        return [
            TransactionArgument(arg, serializer)
            for arg, serializer in zip(arguments, types)
        ]

    def create_transaction_payload(self, payload: dict) -> TransactionPayload:
        try:
            function_information = payload["function"].split("::")
            module = "::".join(function_information[:-1])
            function_id = function_information[-1]
            function_arguments = self.create_transaction_function_arguments(
                payload["functionArguments"], payload["argumentTypes"]
            )
            type_arguments = [
                TypeTag(StructTag.from_str(argument))
                for argument in payload["typeArguments"]
            ]
            entry_function = EntryFunction.natural(
                module=module,
                function=function_id,
                ty_args=type_arguments,
                args=function_arguments,
            )
            return TransactionPayload(payload=entry_function)
        except Exception as e:
            print(f"Error creating transaction payload: {e}")
            raise

    async def submit_transaction(self, transaction_payload: TransactionPayload) -> str:
        try:
            signed_transaction_request = (
                await self.rest_client.create_bcs_signed_transaction(
                    sender=self.account, payload=transaction_payload
                )
            )
            txn_hash = await self.rest_client.submit_bcs_transaction(
                signed_transaction=signed_transaction_request
            )
            await self.rest_client.wait_for_transaction(txn_hash=txn_hash)
            return txn_hash
        except Exception as e:
            print(f"Error during transaction submission: {e}")
            raise


async def deposit(amount: int, user_address: str) -> dict:
    """
    Deposit to your wallet address.

    Args:
        amount (int): The amount to deposit.
        user_address (str): The user's wallet address.

    Returns:
        A Dict of completed deposit transaction.
    """

    NODE_URL = f"{os.environ.get('APTOS_BASE_URL')}"
    rest_client = RestClient(NODE_URL)
    private_key_hex = f"{os.environ.get('PRIVATE_KEY')}"
    if private_key_hex.startswith("0x"):
        private_key_hex = private_key_hex[2:]
    private_key_bytes = bytes.fromhex(private_key_hex)
    account = Account.load_key(private_key_bytes)
    API_URL = f"{os.environ.get('KANA_BASE_URL')}/deposit"
    PARAMS = {
        "userAddress": user_address,  # f"{os.environ.get('WALLET_ADDRESS')}",
        "amount": amount,
    }
    HEADERS = {"x-api-key": os.environ.get("KANA_API_KEY")}
    handler = AptosTransactionHandler(rest_client, account)
    payload_data = handler.fetch_payload(API_URL, PARAMS, HEADERS)

    if not payload_data:
        return {"Error": "Failed to fetch payload data."}

    try:
        payload_data["functionArguments"] = [
            AccountAddress.from_str(payload_data["functionArguments"][0]),
            int(payload_data["functionArguments"][1]),
        ]
        payload_data["argumentTypes"] = [Serializer.struct, Serializer.u64]
        transaction_payload = handler.create_transaction_payload(payload_data)

        txn_hash = await handler.submit_transaction(transaction_payload)

        return {"Result": txn_hash}

    except Exception as e:
        return {"Error during transaction process": e}
        return {"Error": str(e)}
