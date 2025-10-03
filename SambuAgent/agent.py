import warnings, logging, asyncio

import dotenv

dotenv.load_dotenv("../.env")

from google.adk.agents import Agent
from google.adk.tools import LongRunningFunctionTool, google_search


from SambuAgent.SambuTools.deposit import deposit
from SambuAgent.SambuTools.sambuAPI import (
    fetchMarketInfo,
    perpMarketInfo,
    getWalletBalance,
    getWalletAptBalance,
    getProfileAddress,
    getNetProfileBalance,
    getTradeHistory,
    getMarketPrice,
    getLastExecutedPrice,
    getAllOpenOrderIds,
    getPositions,
    getAllTrades,
    getDepositAndWithdrawHistory,
    placeMarketOrder,
    signAndSendTransaction,
    fundAccount,
    getAccountBalance,
    getChainIdsAndData,
)


from SambuAgent.SambuTools.cancelAndPlaceMultipleOrders import (
    cancelAndPlaceMultipleOrders,
)

from SambuAgent.SambuTools.cancelMultipleOrders import cancelMultipleOrders

from SambuAgent.SambuTools.placeMultipleOrders import placeMultipleOrders

from SambuAgent.SambuTools.withdraw import withdraw

from SambuAgent.SambuTools.cancelAndPlaceMultipleOrders import (
    cancelAndPlaceMultipleOrders,
)

from SambuAgent.SambuTools.limitOrder import limitOrder

from SambuAgent.SambuTools.collapsePosition import collapsePosition

from SambuAgent.SambuTools.updateTakeProfit import updateTakeProfit

from SambuAgent.SambuTools.updateStopLoss import updateStopLoss

from SambuAgent.SambuTools.addMargin import addMargin

from SambuAgent.SambuTools.settlePNL import settlePNL

from SambuAgent.SambuTools.buildTransaction import buildTransaction


MODEL = "gemini-2.0-flash"

# Ignore all warnings
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)


root_agent = Agent(
    name="Sambu_Agent",
    model=MODEL,
    description="""You are an advanced trading assistant specialized in KANA Labs perpetual trading on the APTOS blockchain. You help users manage their trading activities, portfolio, and execute various trading operations.""",
    instruction="""
        Your capabilities include:

        Account Management:
        - Check wallet balances (APT and other tokens)
        - View profile address and net balance
        - Monitor deposit and withdrawal history
        - Execute deposits and withdrawals
        - Settle PNL

        Transaction Management:
        - Build Transactions
        - Sign and send Transactions
        - Fund Accounts
        - Get Account Balance

        Chain IDs for Market Analysis
        - Retrieve Chain IDs for market analysis.


        Market Analysis:
        - Fetch real-time market information
        - Get perpetual market details
        - Access current market prices
        - View last executed prices
        - Analyze trade history

        Trading Operations:
        - Place market orders
        - Create limit orders
        - Manage multiple orders (place/cancel)
        - Monitor open positions
        - Collapse positions
        - Add margin to positions
        - Set and update take-profit levels
        - Set and update stop-loss levels

        When interacting with users:
        1. Always verify their intentions clearly before executing trades
        2. Provide relevant market information before suggesting actions
        3. Explain risks associated with perpetual trading
        4. Double-check position sizes and leverage levels
        5. Confirm order details before execution
        6. Monitor position management and risk parameters

        For each action:
        - Explain what you're doing
        - Show relevant market data
        - Confirm user instructions
        - Execute requested operations
        - Provide confirmation and results

        Safety Protocols:
        - Verify wallet balance before trades
        - Check position limits
        - Confirm leverage levels
        - Validate order parameters
        - Ensure stop-loss and take-profit levels are reasonable

        Remember to:
        - Be precise with numbers and calculations
        - Use clear, concise language
        - Prioritize risk management
        - Provide educational context when needed
        - Monitor market conditions actively

        How can I assist you with your KANA Labs perpetual trading today?
    """,
    tools=[
        # google_search,
        LongRunningFunctionTool(func=deposit),
        LongRunningFunctionTool(func=fetchMarketInfo),
        LongRunningFunctionTool(func=perpMarketInfo),
        LongRunningFunctionTool(func=getWalletBalance),
        LongRunningFunctionTool(func=getWalletAptBalance),
        LongRunningFunctionTool(func=getProfileAddress),
        LongRunningFunctionTool(func=getNetProfileBalance),
        LongRunningFunctionTool(func=getTradeHistory),
        LongRunningFunctionTool(func=getMarketPrice),
        LongRunningFunctionTool(func=getLastExecutedPrice),
        LongRunningFunctionTool(func=getAllOpenOrderIds),
        LongRunningFunctionTool(func=getPositions),
        LongRunningFunctionTool(func=getAllTrades),
        LongRunningFunctionTool(func=getDepositAndWithdrawHistory),
        LongRunningFunctionTool(func=placeMarketOrder),
        LongRunningFunctionTool(func=cancelAndPlaceMultipleOrders),
        LongRunningFunctionTool(func=cancelMultipleOrders),
        LongRunningFunctionTool(func=placeMultipleOrders),
        LongRunningFunctionTool(func=withdraw),
        LongRunningFunctionTool(func=collapsePosition),
        LongRunningFunctionTool(func=updateTakeProfit),
        LongRunningFunctionTool(func=updateStopLoss),
        LongRunningFunctionTool(func=limitOrder),
        LongRunningFunctionTool(func=addMargin),
        LongRunningFunctionTool(func=settlePNL),
        LongRunningFunctionTool(func=buildTransaction),
        LongRunningFunctionTool(func=signAndSendTransaction),
        LongRunningFunctionTool(func=fundAccount),
        LongRunningFunctionTool(func=getAccountBalance),
        LongRunningFunctionTool(func=getChainIdsAndData),
    ],
)
