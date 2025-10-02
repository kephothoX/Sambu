import asyncio
import os
import requests
from dotenv import load_dotenv
from typing import List
from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.bcs import Serializer
from aptos_sdk.type_tag import TypeTag, StructTag

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
        except requests.RequestException as e:
            print(f"Error fetching payload: {e}")
            return None

    def create_transaction_function_arguments(
        self, arguments: List, types: List[Serializer]
    ) -> List[TransactionArgument]:
        if len(arguments) != len(types):
            raise ValueError("Arguments and types length mismatch.")
        return [
            TransactionArgument(arg, serializer)
            for arg, serializer in zip(arguments, types)
        ]

    def create_transaction_payload(self, payload: dict) -> TransactionPayload:
        try:
            module, function_id = (
                "::".join(payload["function"].split("::")[:-1]),
                payload["function"].split("::")[-1],
            )
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
            signed_transaction = await self.rest_client.create_bcs_signed_transaction(
                self.account, transaction_payload
            )
            txn_hash = await self.rest_client.submit_bcs_transaction(signed_transaction)
            await self.rest_client.wait_for_transaction(txn_hash)
            return txn_hash
        except Exception as e:
            print(f"Error during transaction submission: {e}")
            raise


async def addMargin(
    private_key: str, market_id: int, trade_side: bool, amount: int
) -> dict:
    """
    Add margin to a specific market.

    Args:
        private_key (str): The private key of the user.
        market_id (int): The ID of the market.
        trade_side (bool): True for long, False for short.
        amount (int): The amount of margin to add.

    Returns:
        dict: A dictionary containing the result of the transaction.
    """

    NODE_URL = f"{os.environ.get('APTOS_BASE_URL')}"
    rest_client = RestClient(NODE_URL)
    private_key_hex = private_key

    if not private_key_hex:
        print("Error: APTOS_PRIVATEKEY is missing in .env file.")
        return

    account = Account.load_key(
        bytes.fromhex(
            private_key_hex[2:] if private_key_hex.startswith("0x") else private_key_hex
        )
    )
    rest_client = RestClient(NODE_URL)

    API_URL = f"{os.environ.get('KANA_BASE_URL')}/addMargin"
    PARAMS = {"marketId": market_id, "tradeSide": trade_side, "amount": amount}
    HEADERS = {"x-api-key": os.environ.get("KANA_API_KEY")}

    handler = AptosTransactionHandler(rest_client, account)
    payload_data = handler.fetch_payload(API_URL, PARAMS, HEADERS)

    if not payload_data:
        return {"Error": "Failed to fetch payload data."}

    try:
        payload_data["functionArguments"] = [
            int(payload_data["functionArguments"][0]),
            payload_data["functionArguments"][1].lower() == "true",
            int(payload_data["functionArguments"][2]),
        ]

        payload_data["argumentTypes"] = [
            Serializer.u64,
            Serializer.bool,
            Serializer.u64,
        ]

        transaction_payload = handler.create_transaction_payload(payload_data)

        txn_hash = await handler.submit_transaction(transaction_payload)
        return {"Transaction submitted successfully. Hash": txn_hash}

    except Exception as e:
        return {"Error Transaction process error": e}
