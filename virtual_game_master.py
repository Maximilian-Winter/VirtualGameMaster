import datetime
import json
import os

from typing import Tuple, Generator

from game_state import GameState
from config import VirtualGameMasterConfig
from message_template import MessageTemplate
from chat_api import ChatAPI
from chat_history import ChatHistory, Message, ChatFormatter

from command_system import CommandSystem
import commands


class VirtualGameMaster:
    def __init__(self, config: VirtualGameMasterConfig, api: ChatAPI, debug_mode: bool = False):
        self.config = config
        CommandSystem.command_prefix = self.config.COMMAND_PREFIX
        self.api = api
        self.system_message_template = MessageTemplate.from_file(
            config.SYSTEM_MESSAGE_FILE
        )
        self.save_system_message_template = MessageTemplate.from_file(
            config.SAVE_SYSTEM_MESSAGE_FILE
        )

        self.game_state = GameState(config.INITIAL_GAME_STATE)
        self.history = ChatHistory(config.GAME_SAVE_FOLDER)
        self.history_offset = 0

        self.debug_mode = debug_mode
        self.next_message_id = 0
        self.max_messages = config.MAX_MESSAGES
        self.kept_messages = config.KEPT_MESSAGES

    def process_input(self, user_input: str, stream: bool) -> Tuple[str, bool] | Tuple[
        Generator[str, None, None], bool]:

        if user_input.startswith(CommandSystem.command_prefix):
            return CommandSystem.handle_command(self, user_input)

        if stream:
            return self.get_streaming_response(user_input), False
        return self.get_response(user_input), False

    def get_response(self, user_input: str) -> str:
        history = self.pre_response(user_input)
        response = self.api.get_response(history)
        self.post_response(response)

        return response.strip()

    def get_streaming_response(self, user_input: str) -> Generator[str, None, None]:
        history = self.pre_response(user_input)
        full_response = ""
        for response_chunk in self.api.get_streaming_response(history):
            full_response += response_chunk
            yield response_chunk
        self.post_response(full_response)

    def pre_response(self, user_input: str) -> list[dict[str, str]]:
        self.history.add_message(Message("user", user_input.strip(), self.next_message_id))
        self.next_message_id += 1

        history = self.history.to_list()
        history = history[self.history_offset:]
        history.insert(0, {"role": "system",
                           "content": self.get_current_system_message()})

        if self.debug_mode:
            print(history[0]["content"])

        return history

    def get_current_system_message(self):
        return self.system_message_template.generate_message_content(
            self.game_state.template_fields).strip()

    def format_history(self, history: list[dict[str, str]]) -> str:
        template = "{role}: {content}\n\n"
        role_names = {
            "assistant": "Game Master",
            "user": "Player"
        }
        formatter = ChatFormatter(template, role_names)

        if len(history) > 0:
            output = "History:\n"
            output += formatter.format_messages(history)
        else:
            output = "History is empty.\n"

        return output

    def get_complete_history_formatted(self):
        history = self.history.to_list()
        return self.format_history(history=history)

    def get_current_history_formatted(self):
        history = self.get_currently_used_history()
        return self.format_history(history=history)

    def post_response(self, response: str) -> None:
        self.history.add_message(Message("assistant", response.strip(), self.next_message_id))
        self.next_message_id += 1
        self.history.save_history()

        if len(self.history.messages) - self.history_offset >= self.max_messages:
            self.generate_save_state()

    def edit_message(self, message_id: int, new_content: str) -> bool:
        success = self.history.edit_message(message_id, new_content)
        if success:
            self.history.save_history()
        return success

    def manual_save(self):
        self.generate_save_state()

    def get_currently_used_history(self):
        history = self.history.to_list()[self.history_offset:]
        return history

    def generate_save_state(self):
        history = self.history.to_list()[self.history_offset:]

        template = "{role}: {content}\n\n"
        role_names = {
            "assistant": "Game Master",
            "user": "Player"
        }
        formatter = ChatFormatter(template, role_names)
        formatted_chat = formatter.format_messages(history)

        prompt = self.save_system_message_template.generate_message_content(
            template_fields=self.game_state.template_fields,
            CHAT_HISTORY=formatted_chat)

        print(prompt)
        settings = self.api.get_default_settings()
        settings.temperature = 0.65

        settings.top_p = 0.95
        settings.top_k = 50
        settings.min_p = 0.05
        settings.tfs_z = 0.9

        settings.max_tokens = 4096
        prompt_message = [{"role": "system",
                           "content": "You are an AI assistant tasked with updating the game state of a text-based role-playing game."},
                          {"role": "user", "content": prompt}]
        response_gen = self.api.get_streaming_response(prompt_message, settings)

        full_response = ""
        for response_chunk in response_gen:
            full_response += response_chunk
            print(response_chunk, end="", flush=True)

        if self.debug_mode:
            print(f"Update game info:\n{full_response}")

        self.game_state.update_from_xml(full_response)
        self.history_offset = len(self.history.messages) - self.kept_messages

        self.save()

    def save(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_id = f"{timestamp}"
        filename = f"save_state_{save_id}.json"
        save_data = {
            "settings": self.api.get_current_settings().to_dict(),
            "template_fields": self.game_state.template_fields,
            "history_offset": self.history_offset,
            "next_message_id": self.next_message_id
        }
        with open(f"{self.config.GAME_SAVE_FOLDER}/{filename}", "w") as f:
            json.dump(save_data, f)

    def load(self):
        self.history.load_history()
        self.next_message_id = max([msg.id for msg in self.history.messages], default=-1) + 1

        save_files = [f for f in os.listdir(self.config.GAME_SAVE_FOLDER) if
                      f.startswith("save_state_") and f.endswith(".json")]

        if not save_files:
            print("No save state found. Starting a new game.")
            return

        # Sort save files based on the timestamp in the filename
        latest_save = sorted(save_files, reverse=True)[0]

        try:
            with open(f"{self.config.GAME_SAVE_FOLDER}/{latest_save}", "r") as f:
                save_data = json.load(f)
            self.game_state.template_fields = save_data.get("template_fields", self.game_state.template_fields)
            self.history_offset = save_data.get("history_offset", 0)
            self.next_message_id = save_data.get("next_message_id", self.next_message_id)
            print(f"Loaded the most recent game state: {latest_save}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading save state: {e}. Starting a new game.")
