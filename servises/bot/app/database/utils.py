import json
import os
import logging

logger = logging.getLogger(__name__)

# Correct path to the messages.json file
MESSAGES_PATH = os.path.join(
    os.path.dirname(__file__),
    "damp", "messages", "message.json"
)

async def load_initial_messages(db_service):
    if not os.path.exists(MESSAGES_PATH):
        logger.warning(f"File not found, skipping message dump: {MESSAGES_PATH}")
        return

    try:
        with open(MESSAGES_PATH, 'r', encoding='utf-8') as f:
            messages_data = json.load(f)
            for msg_id, msg_data in messages_data.items():
                await db_service.add_message(
                    message_id=msg_id,
                    text=msg_data.get("text"),
                    media=msg_data.get("media"),
                    keyboard=msg_data.get("keyboard")
                )
        logger.info("Initial messages from JSON file loaded/updated in the database.")
    except Exception as e:
        logger.error(f"An error occurred while loading messages from JSON: {e}", exc_info=True)