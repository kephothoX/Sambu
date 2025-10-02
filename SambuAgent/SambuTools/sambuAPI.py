import requests, os

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


BASE_URL = f"{os.environ.get('KANA_BASE_URL')}"
API_KEY = f"{os.environ.get('KANA_API_KEY')}"
USER_ADDRESS = f"{os.environ.get('WALLET_ADDRESS')}"
APTOS_URL = f"{os.environ.get('APTOS_BASE_URL')}"
ASSET_TYPE = "0x1::aptos_coin::AptosCoin"

NODE_URL = "https://fullnode.devnet.aptoslabs.com/v1"
FAUCET_URL = "https://faucet.devnet.aptoslabs.com"

rest_client = RestClient(NODE_URL)
faucet_client = FaucetClient(FAUCET_URL, rest_client)


def generateNewAPTOsAccount() -> dict:
    account = Account.generate()

    return {"APTOS Account": account}


async def simulateTransaction(
    sender_address: str, receiver_address: str, amount: int
) -> dict:
    """
    Simulate a transaction from one account to another.

    Args:
        sender_address (str): The sender's account address.
        receiver_address (str): The receiver's account address.
        amount (int): The amount to transfer.

    Returns:
        dict: A dictionary containing the simulation result.
    """

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
                    account.address(), Serializer.struct
                ),  # Recipient address
                TransactionArgument(
                    amount, Serializer.u64
                ),  # Amount to transfer (1000 octas)
            ],
        )

        simulation_transaction = await rest_client.create_bcs_transaction(
            account.address(), TransactionPayload(entry_function)
        )

        # Simulate the transaction to estimate gas costs and check for errors
        simulation_result = await rest_client.simulate_transaction(
            simulation_transaction, Account.load_key(sender_address)
        )

        # Extract and display the simulation results
        gas_used = int(simulation_result[0]["gas_used"])
        gas_unit_price = int(simulation_result[0]["gas_unit_price"])
        success = simulation_result[0]["success"]

        response = {
            "Simulation Result": simulation_result,
            "Gas Used": gas_used,
            "Gas Unit Price": gas_unit_price,
            "Success": success,
        }

        return {"Simulation Result": response}

    except Exception as e:
        return {"Error": f"An error occurred:, {e}"}


async def signAndSendTransaction(sender_address: str, amount: int) -> dict:
    try:
        private_key_hex = sender_address
        if private_key_hex.startswith("0x"):
            private_key_hex = private_key_hex[2:]
        private_key_bytes = bytes.fromhex(private_key_hex)
        account = Account.load_key(private_key_bytes)

        account_data = await rest_client.account(account.address())
        sequence_number = int(account_data["sequence_number"])

        entry_function = EntryFunction.natural(
            "0x1::aptos_account",  # Module address and name
            "transfer",  # Function name
            [],  # Type arguments (empty for this function)
            [
                # Function arguments with their serialization type
                TransactionArgument(
                    account.address(), Serializer.struct
                ),  # Recipient address
                TransactionArgument(
                    amount, Serializer.u64
                ),  # Amount to transfer (1000 octas)
            ],
        )

        signed_transaction = await rest_client.create_bcs_signed_transaction(
            account.address(),  # Account with the private key
            TransactionPayload(entry_function),  # The payload from our transaction
            sequence_number=sequence_number,  # Use the same sequence number as before
        )

        tx_hash = await rest_client.submit_bcs_transaction(signed_transaction)

        await rest_client.wait_for_transaction(tx_hash)

        # Get the transaction details to check its status
        transaction_details = await rest_client.transaction_by_hash(tx_hash)
        success = transaction_details["success"]
        vm_status = transaction_details["vm_status"]
        gas_used = transaction_details["gas_used"]

        response = {
            "VM  Status": vm_status,
            "Gas Used": gas_used,
            "Success": success,
        }

        return {"Transaction completed with status": response}

    except Exception as e:
        return {"Error": f"An error occurred:, {e}"}


async def fundAccount(wallet_address: str, amount: int) -> dict:
    response = await faucet_client.fund_account(
        Account.load_key(wallet_address), amount
    )

    return {"Account Funded": response}


async def getAccountBalance(wallet_address: str) -> dict:
    balance = await rest_client.account_balance(Account.load_key(wallet_address))

    return {"Balance in Octas": balance}


def fetchMarketInfo(market_id: int) -> dict:
    """
    Fetch market information for a given market ID.

    Args:
        market_id (int): The market ID.

    Returns:
        dict: A dictionary containing the market information.
    """

    try:
        params = {"marketId": market_id}
        headers = {"x-api-key": API_KEY}
        response = requests.get(
            f"{BASE_URL}/getMarketInfo", params=params, headers=headers
        )
        response.raise_for_status()
        get_market_info = response.json()
        return {"getMarketInfo": get_market_info}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def perpMarketInfo(market_id: int) -> dict:
    try:
        params = {"marketId": market_id}
        headers = {"x-api-key": API_KEY}
        response = requests.get(
            f"{BASE_URL}/getPerpetualAssetsInfo", params=params, headers=headers
        )
        response.raise_for_status()
        perp_market_info = response.json()
        return {"Perp market Info": perp_market_info}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getWalletBalance(wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"userAddress": wallet_address}

        response = requests.get(
            f"{APTOS_URL}/accounts/{USER_ADDRESS}/balance/{ASSET_TYPE}",
            headers=headers,
        )
        response.raise_for_status()
        walletBalance = response.json()
        return {"Wallet Balance": walletBalance}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getWalletAptBalance(wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getAccountAptBalance",
            params=params,
            headers=headers,
        )

        response.raise_for_status()
        walletAptosBalance = response.json()
        return {"Wallet Aptos Balance": walletAptosBalance}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


"""def getNetProfileBalance():
    try:
        headers = {"x-api-key": API_KEY}
        params = {"userAddress": USER_ADDRESS}

        response = requests.get(
            f"{BASE_URL}getAccountAptBalance",
            params=params,
            headers=headers,
        )

        response.raise_for_status()
        walletAptosBalance = response.json()
        print("Wallet Aptos Balance: : ", walletAptosBalance)
    except requests.exceptions.RequestException as error:
        print("An error occurred:", error)
"""


def getProfileAddress(wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getProfileAddress",
            params=params,
            headers=headers,
        )

        response.raise_for_status()
        profileAddress = response.json()
        return {"Profile Address": profileAddress}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getNetProfileBalance(wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getNetProfileBalance",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        netProfileBalance = response.json()
        return {"Net Profile Balance": netProfileBalance}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getTradeHistory(wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getTradeHistory",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        tradeHistory = response.json()
        return {"Trade History": tradeHistory}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getMarketPrice(market_id: int) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"marketId": market_id}

        response = requests.get(
            f"{BASE_URL}/getMarketPrice",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        marketPrice = response.json()
        return {"Market Price": marketPrice}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getLastExecutedPrice(market_id: int) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"marketId": market_id}

        response = requests.get(
            f"{BASE_URL}/getLastPlacedPrice",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        marketPrice = response.json()
        return {"Market Price": marketPrice}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getAllOpenOrderIds(market_id: int, wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"marketId": market_id, "userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getAllOpenOrderIds",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        openOrderIds = response.json()
        return {"Open Order IDs": openOrderIds}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getPositions(market_id: int, wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"marketId": market_id, "userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getPositions",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        positons = response.json()
        return {"Positions": positons}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getFills(market_id: int, wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"marketId": market_id, "userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getFills",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        fills = response.json()
        return {"Fills": fills}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getOrdersFromContract(market_id: int, wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"marketId": market_id, "userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getOpenOrdersFromContract",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        open_orders_from_contract = response.json()
        return {"Open Orders From Contract": open_orders_from_contract}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getOrdersStatusById(market_id: int, order_id: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"marketId": market_id, "orderId": order_id}

        response = requests.get(
            f"{BASE_URL}/fetchOrderStatusById",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        order_status_by_id = response.json()
        return {"Order Status By Id": order_status_by_id}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getFundingHistory(wallet_address: str) -> dict:
    """
    Get funding history for a given wallet address.

    Args:
        wallet_address (str): The wallet address.

    Returns:
        dict: A dictionary containing the funding history.
    """

    try:
        headers = {"x-api-key": API_KEY}
        params = {"userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getFundingHistory",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        funding_history = response.json()
        return {"Funding History": funding_history}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getPositionsFromContract(market_id: int, wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"marketId": market_id, "userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getPositionsFromContract",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        open_orders_from_contract = response.json()
        return {"Open Orders From Contract": open_orders_from_contract}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getAllTrades(market_id: int) -> dict:
    try:
        params = {"marketId": market_id}
        headers = {"x-api-key": API_KEY}
        response = requests.get(
            f"{BASE_URL}/getAllTrades", params=params, headers=headers
        )
        response.raise_for_status()
        get_all_trades = response.json()
        return {"Get All Trades": get_all_trades}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def getDepositAndWithdrawHistory(wallet_address: str) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {"userAddress": wallet_address}

        response = requests.get(
            f"{BASE_URL}/getDepositAndWithdrawHistory",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        depositAndWithdrawHistory = response.json()
        return {"Deposit And Withdraw History": depositAndWithdrawHistory}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}


def placeMarketOrder(
    market_id: str, trade_side: bool, direction: bool, size: int, leverage: int
) -> dict:
    try:
        headers = {"x-api-key": API_KEY}
        params = {
            "marketId": market_id,
            "tradeSide": trade_side,
            "direction": direction,
            "size": size,
            "leverage": leverage,
        }

        response = requests.get(
            f"{BASE_URL}/placeMarketOrder",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        marketOrder = response.json()
        return {"Market Order": marketOrder}
    except requests.exceptions.RequestException as error:
        return {"Error": f"An error occurred:, {error}"}
