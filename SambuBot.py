#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

import os, uuid, asyncio

import uvicorn

from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner

from google.adk.sessions import InMemorySessionService, Session

from google.genai import types

from SambuAgent.agent import root_agent


import logging, os

from dotenv import load_dotenv

load_dotenv(".env")


from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()


APP_NAME = "SambuAgent"
USER_ID = str(uuid.uuid4())
SESSION_ID = str(uuid.uuid4())  # Using a fixed ID for simplicity
SESSION = None


async def initialize_session():
    SESSION = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    SESSION_ID = SESSION.id
    print(f"Session:  {SESSION}")
    # await memory_service.add_session_to_memory(session=SESSION)
    return SESSION, SESSION_ID


SESSION, SESSION_ID = asyncio.run(initialize_session())
QUERY = range(1)

runner = Runner(
    agent=root_agent,  # The agent we want to run
    app_name=APP_NAME,  # Associates runs with our app
    session_service=session_service,  # Uses our session manager
)

TOKEN = f"{os.environ.get('SAMBUBOT_TOKEN')}"
print(TOKEN)


async def call_agent(runner, user_id, session_id, query):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    root_agent.run_async

    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif (
                event.actions and event.actions.escalate
            ):  # Handle potential errors/escalations
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")
    print(f"Response:  {final_response_text}")
    return final_response_text


def retrieve_agent_reply(_runner, _user_id, _session_id, _query) -> str:
    response = asyncio.run(call_agent(_runner, _user_id, _session_id, _query))
    return response


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    await update.message.reply_text(
        "Hi! My name is Professor Sambu with expertise in APTOS and KANA labs web3 platforms. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "How can  help you today?",
        reply_markup=ReplyKeyboardRemove(),
    )

    return QUERY


async def query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores query and processes output."""
    user = update.message.from_user
    logger.info("Query from %s: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        await call_agent(runner, USER_ID, SESSION_ID, update.message.text),
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.WAITING


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, query)],
            # RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, response)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=100000000000000000000000000000000000000000,
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
