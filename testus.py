import datetime
import json
import os
from typing import Dict, Any, List


class ChatFormatter:
    def __init__(self, template, role_names: Dict[str, str] = None):
        self.template = template
        self.role_names = role_names or {}

    def format_messages(self, messages):
        formatted_chat = []
        for message in messages:
            role = message['role']
            content = message['content']
            display_name = self.role_names.get(role, role.capitalize())
            formatted_message = self.template.format(role=display_name, content=content)
            formatted_chat.append(formatted_message)
        return '\n'.join(formatted_chat)


class Message:
    def __init__(self, role: str, content: str, message_id: int = None):
        self.role = role
        self.content = content
        self.id = message_id

    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content, "id": self.id}


class ChatHistory:
    def __init__(self, history_folder: str):
        self.messages: List[Message] = []
        self.history_folder = history_folder

    def add_message(self, message: Message):
        self.messages.append(message)

    def edit_message(self, message_id: int, new_content: str) -> bool:
        for message in self.messages:
            if message.id == message_id:
                message.content = new_content
                return True
        return False

    def to_list(self) -> List[Dict[str, Any]]:
        return [message.to_dict() for message in self.messages]

    def assign_message_ids(self) -> None:
        """Assign incremental IDs to messages that don't have them."""
        next_id = 0
        for message in self.messages:
            if message.id is None:
                message.id = next_id
                next_id += 1
            else:
                next_id = max(next_id, message.id + 1)

    def save_history(self):
        if not os.path.exists(self.history_folder):
            os.makedirs(self.history_folder)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_id = f"{timestamp}"
        filename = f"chat_history_{save_id}.json"

        with open(f"{self.history_folder}/{filename}", "w") as f:
            json.dump(self.to_list(), f)

    def load_history(self):
        if not os.path.exists(self.history_folder):
            os.makedirs(self.history_folder)
            print("No chat history found. Starting with an empty history.")
            self.messages = []
            return

        history_files = [f for f in os.listdir(self.history_folder) if
                         f.startswith("chat_history_") and f.endswith(".json")]

        if not history_files:
            print("No chat history found. Starting with an empty history.")
            self.messages = []
            return

        # Sort history files based on the timestamp in the filename
        latest_history = sorted(history_files, reverse=True)[0]

        try:
            with open(f"{self.history_folder}/{latest_history}", "r") as f:
                loaded_history = json.load(f)
                self.messages = [Message(msg['role'], msg['content'], msg.get('id')) for msg in loaded_history]
            print(f"Loaded the most recent chat history: {latest_history}")
            self.assign_message_ids()  # Ensure all messages have IDs
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading chat history: {e}. Starting with an empty history.")
            self.messages = []


history = ChatHistory("chat_history/new_gameClaude")
history.load_history()
messages = history.to_list()

template = "{role}: {content}\n---"
role_names = {
    "assistant": "Game Master",
    "user": "Player"
}
formatter = ChatFormatter(template, role_names)
formatted_chat = formatter.format_messages(messages)
# print(formatted_chat.strip())

import difflib


def generate_diff_example(old_content, new_content):
    """Generate a diff example to show the LLM."""
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile="old",
        tofile="new",
        lineterm="\n"
    )
    return ''.join(diff)


print(generate_diff_example("Hello, World!\nHello, World!\nHello, World!\n",
                            "Hello, World.\nHello, World.\nHello, World.\n"))
