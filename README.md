# Sambu - The KANA Labs Trading Assistant

Sambu is an advanced, conversational trading assistant designed for the KANA Labs perpetual trading platform on the APTOS blockchain. It operates as a Telegram bot, leveraging the power of Google's Gemini Pro model to provide a seamless and interactive trading experience.

## 🚀 Features

Sambu is equipped with a wide range of capabilities to help you manage your trading activities effectively.

### Account Management

- **Wallet Balances**: Check your APT and other token balances.
- **Profile Information**: View your profile address and net balance.
- **Transaction History**: Monitor your deposit and withdrawal history.
- **Funds Management**: Execute deposits, withdrawals, and settle PNL.

### Market Analysis

- **Real-time Data**: Fetch live market information and perpetual market details.
- **Price Checks**: Get current market prices and the last executed prices.
- **Trade History**: Analyze historical trade data.

### Trading Operations

- **Order Placement**: Place market and limit orders.
- **Order Management**: Place, cancel, and manage multiple orders at once.
- **Position Monitoring**: Keep track of all your open positions and order IDs.
- **Risk Management**: Collapse positions, add margin, and update take-profit/stop-loss levels.

### Transaction Handling

- **On-Chain Interaction**: Build, sign, and send transactions directly on the Aptos network.
- **Account Funding**: Fund your trading account.

## 🛠️ Architecture

The project consists of three main components:

1. **Telegram Bot (`SambuBot.py`)**: The user-facing interface built with `python-telegram-bot`. It handles user messages and manages the conversation flow.
2. **ADK Agent (`SambuAgent/agent.py`)**: The core logic, built using the Google Agent Development Kit (ADK). This `LlmAgent` uses the `gemini-2.0-flash` model to understand user intent and decide which tool to use.
3. **Trading Tools (`SambuAgent/SambuTools/`)**: A collection of Python functions that implement the agent's capabilities by interacting with the KANA Labs and Aptos blockchain APIs.

When a user sends a message on Telegram, the bot passes it to the ADK Agent. The agent processes the query, calls the appropriate tool(s) to perform the requested action, and returns a natural language response to the user.

## ⚙️ Getting Started

Follow these steps to set up and run your own instance of the Sambu bot.

### Prerequisites

- Python 3.9+
- A Telegram Bot Token. You can get one from BotFather.

### Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/kephothoX/Sambu.git
    cd Sambu
    ```

2. **Create a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    *(Note: A `requirements.txt` file is recommended. Based on the code, you will need the following packages.)*

    ```sh
    pip install python-telegram-bot google-generativeai google-adk python-dotenv uvicorn
    ```

### Configuration

1. Create a file named `.env` in the root directory of the project.
2. Add your Telegram bot token to the `.env` file:

    ```
    KANA_API_KEY=Byd1IAXsV2ZvJFSEft49AeFDeZjsUNJ6Hf8GxvG1Snj5QpeO

    KANA_BASE_URL=<https://perps-tradeapi.kanalabs.io>
    APTOS_BASE_URL=<https://api.testnet.aptoslabs.com/v1>
    WALLET_ADDRESS="YOUR WALLET ADDRESS HERE"
    PRIVATE_KEY="YOUR PRIVATE KEY HERE"
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY="YOUR GOOGLE API KEY HERE (FROM GOOGLE AI STUDIO)"
    SAMBUBOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"

    ```

3. You may also need to add other API keys or private keys for interacting with the Aptos network, depending on the implementation of the functions in `SambuAgent/SambuTools/`.

### Running the Bot

Execute the main bot file to start the application:

```sh
python SambuBot.py
```

Once running, open Telegram and start a conversation with your bot by sending the `/start` command.
Use `/cancel` to stop the conversation.

### Using Google ADK Web

Run `adk web` from parent folder then open your browser with `http://localhost:8000` as URL

## 📂 Project Structure

```
Sambu/
├── .env                  # Environment variables (API keys, tokens)
├── SambuBot.py           # Main application entry point - The Telegram Bot
├── SambuAgent/
│   ├── agent.py          # Defines the core ADK LlmAgent and its tools
│   └── SambuTools/       # Directory for all trading and blockchain functions
│       ├── sambuAPI.py
│       └── ...           # Other tool files
└── README.md             # This file
```
