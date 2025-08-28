from typing import List
from app.src.domain.chat import ChatMessage
from app.src.utils.logs import logger

class ChatHistoryProcessor:
    def __init__(self):
        self.max_history_length = 10

    def format_chat_history(self, chat_history: List[ChatMessage]) -> str:
        try:
            if not chat_history:
                logger.debug("No chat history provided")
                return ""

            if len(chat_history) > self.max_history_length:
                chat_history = chat_history[-self.max_history_length:]
                logger.debug(f"Truncated chat history to last {self.max_history_length} messages")

            formatted_history = []
            for message in chat_history:
                if message.role == "user":
                    formatted_history.append(f"User: {message.content}")
                elif message.role == "assistant":
                    formatted_history.append(f"Assistant: {message.content}")

            history_text = "\n".join(formatted_history)
            logger.debug(f"Formatted chat history with {len(chat_history)} messages")
            return history_text

        except Exception as e:
            logger.error(f"Error formatting chat history: {str(e)}")
            return ""

    def extract_relevant_context(self, chat_history: List[ChatMessage]) -> str:
        try:
            formatted_history = self.format_chat_history(chat_history)
            if formatted_history:
                logger.info("Using chat history for context enhancement")
                return f"\n\n# Previous Conversation:\n{formatted_history}\n"

            return ""

        except Exception as e:
            logger.error(f"Error extracting relevant context: {str(e)}")
            return ""
