import asyncio, os, time
from aptos_sdk.account import Account

from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionPayload,
    TransactionArgument,
    RawTransaction,
)
from aptos_sdk.bcs import Serializer

from dotenv import load_dotenv

load_dotenv("../.env")


# Network configuration
NODE_URL = "https://fullnode.devnet.aptoslabs.com/v1"
FAUCET_URL = "https://faucet.devnet.aptoslabs.com"

rest_client = RestClient(NODE_URL)
faucet_client = FaucetClient(FAUCET_URL, rest_client)


async def buildTransaction(
    sender_address: str, receiver_address: str, amount: int
) -> dict:
    try:
        private_key_hex = sender_address
        if private_key_hex.startswith("0x"):
            private_key_hex = private_key_hex[2:]
        private_key_bytes = bytes.fromhex(private_key_hex)
        account = Account.load_key(private_key_bytes)

        entry_function = EntryFunction.natural(
            "0x1::aptos_account",  # Module address and name
            "transfer",  # Function name
            [],  # Type arguments (empty for this function)
            [
                # Function arguments with their serialization type
                TransactionArgument(
                    Account.load_key(receiver_address), Serializer.struct
                ),  # Recipient address
                TransactionArgument(
                    amount, Serializer.u64
                ),  # Amount to transfer (1000 octas)
            ],
        )

        # Get the chain ID for the transaction
        chain_id = await rest_client.chain_id()

        account_data = await rest_client.account(account.address())
        sequence_number = int(account_data["sequence_number"])

        # Create the raw transaction with all required fields
        raw_transaction = RawTransaction(
            sender=account.address(),  # Sender's address
            sequence_number=sequence_number,  # Sequence number to prevent replay attacks
            payload=TransactionPayload(entry_function),  # The function to call
            max_gas_amount=2000,  # Maximum gas units to use
            gas_unit_price=100,  # Price per gas unit in octas
            expiration_timestamps_secs=int(time.time()) + 600,  # Expires in 10 minutes
            chain_id=chain_id,  # Chain ID to ensure correct network
        )

        response = {
            "Sender": raw_transaction.sender,
            "Sequence Number": raw_transaction.sequence_number,
            "Max Gas Amount": raw_transaction.max_gas_amount,
            "Gas Unit Price": raw_transaction.gas_unit_price,
            "Expiration Timestamp": time.ctime(
                raw_transaction.expiration_timestamps_secs
            ),
        }

        return {"Transaction built successfully": response}

    except Exception as e:
        return {"Error": f"An error occurred:, {e}"}
