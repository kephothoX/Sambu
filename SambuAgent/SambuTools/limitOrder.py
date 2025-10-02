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


async def limitOrder(
    private_key: str,
    market_id: int,
    trade_side: bool,
    direction: bool,
    size: int,
    price: int,
    leverage: int,
) -> dict:
    """
    Place a limit order.

    Args:
        private_key (str): The private key of the user.
        market_id (int): The ID of the market.
        trade_side (bool): True for long, False for short.
        direction (bool): True for buy, False for sell.
        size (int): The size of the order.
        price (int): The price of the order.
        leverage (int): The leverage of the order.

    Returns:
        dict: A dictionary containing the result of the transaction.
    """

    NODE_URL = f"{os.environ.get('APTOS_BASE_URL')}"

    private_key_hex = private_key

    if private_key_hex.startswith("0x"):
        private_key_hex = private_key_hex[2:]
    private_key_bytes = bytes.fromhex(private_key_hex)
    account = Account.load_key(private_key_bytes)
    rest_client = RestClient(NODE_URL)

    API_URL = f"{os.environ.get('KANA_BASE_URL')}/placeLimitOrder"
    PARAMS = {
        "marketId": market_id,
        "tradeSide": trade_side,
        "direction": direction,
        "size": size,
        "price": price,
        "leverage": leverage,
    }
    HEADERS = {"x-api-key": os.environ.get("KANA_API_KEY")}

    handler = AptosTransactionHandler(rest_client, account)
    payload_data = handler.fetch_payload(API_URL, PARAMS, HEADERS)

    if not payload_data:
        print("Failed to fetch payload data.")
        return {"Error": "Failed to fetch payload data."}

    try:
        payload_data["functionArguments"] = [
            int(payload_data["functionArguments"][0]),
            payload_data["functionArguments"][1].lower() == "true",
            payload_data["functionArguments"][2].lower() == "true",
            *map(int, payload_data["functionArguments"][3:]),
        ]

        payload_data["argumentTypes"] = [
            Serializer.u64,
            Serializer.bool,
            Serializer.bool,
            Serializer.u64,
            Serializer.u64,
            Serializer.u64,
            Serializer.u8,
            Serializer.u64,
            Serializer.u64,
        ]

        transaction_payload = handler.create_transaction_payload(payload_data)

        txn_hash = await handler.submit_transaction(transaction_payload)

        return {"Transaction submitted successfully. Hash": txn_hash}

    except Exception as e:
        return {"Error": f"An error occurred:, {e}"}
