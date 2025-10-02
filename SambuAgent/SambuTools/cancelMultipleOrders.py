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
from aptos_sdk.type_tag import TypeTag, StructTag
import requests
from dotenv import load_dotenv
from typing import Any, List

load_dotenv()


class AptosTransactionHandler:

    def __init__(self, rest_client: RestClient, account: Account):
        self.rest_client = rest_client
        self.account = account

    def fetch_payload(self, api_url, json_data, headers):
        try:
            response = requests.post(api_url, json=json_data, headers=headers)
            response.raise_for_status()
            payload_data = response.json().get("data")
            if payload_data is None:
                print("No data returned from API.")
                return {}

            # Convert order ID from float to integer
            payload_data["functionArguments"][1] = [
                int(x) for x in payload_data["functionArguments"][1]
            ]

            return payload_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching payload: {e}")
            return None

    def create_transaction_function_arguments(
        self, arguments: List[Any], types: List[Serializer]
    ) -> List[TransactionArgument]:
        if len(arguments) != len(types):
            raise ValueError("Arguments and types length mismatch.")

        try:
            return [
                TransactionArgument(arg, serializer)
                for arg, serializer in zip(arguments, types)
            ]
        except Exception as e:
            print(f"Error creating transaction arguments: {e}")
            raise

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


async def cancelMultipleOrders(
    private_key: str,
    market_id: int,
    order_ids: list[int],
    order_sides: list[bool],
) -> dict:
    """
    Cancel multiple orders.

    Args:
        private_key (str): Private key of the account.
        market_id (int): Market ID.
        order_ids (list[int]): List of order IDs to cancel.
        order_sides (list[bool]): List of order sides.

    Returns:
        dict: Transaction submission result.
    """

    NODE_URL = f"{os.getenv('APTOS_BASE_URL')}/v1"
    rest_client = RestClient(NODE_URL)
    private_key_hex = private_key
    if private_key_hex.startswith("0x"):
        private_key_hex = private_key_hex[2:]
    private_key_bytes = bytes.fromhex(private_key_hex)
    account = Account.load_key(private_key_bytes)

    API_URL = f"{os.environ.get('KANA_BASE_URL')}/cancelMultipleOrders"
    BODY = {
        "marketId": market_id,
        "cancelOrderIds": order_ids,  # pls ensure cancelOrderIds given in string
        "orderSides": order_sides,
    }
    HEADERS = {"x-api-key": os.environ.get("KANA_API_KEY")}
    handler = AptosTransactionHandler(rest_client, account)
    payload_data = handler.fetch_payload(API_URL, BODY, HEADERS)
    if not payload_data:
        return {"Error": "Failed to fetch payload data."}

    try:
        payload_data["argumentTypes"] = [
            Serializer.u64,
            Serializer.sequence_serializer(Serializer.u128),
            Serializer.sequence_serializer(Serializer.bool),
        ]
        transaction_payload = handler.create_transaction_payload(payload_data)

        txn_hash = await handler.submit_transaction(transaction_payload)
        return {f"Transaction submitted successfully. Transaction hash": txn_hash}

    except Exception as e:
        return {"Error": f"An error occurred:, {e}"}
