import os
from dotenv import load_dotenv
from llama_cpp_agent import MessagesFormatterType
from virtual_game_master import VirtualGameMasterConfig, VirtualGameMaster
from chat_api import LlamaAgentProvider, OpenAIChatAPI, OpenRouterAPIPromptMode

load_dotenv()

def display_recent_messages(app: VirtualGameMaster, num_messages: int = 4):
    recent_messages = app.history.messages[-num_messages:]
    for message in recent_messages:
        role = "Game Master" if message.role == "assistant" else "You"
        print(f"{role}: {message.content}\n")

def run_cli(app: VirtualGameMaster):
    app.load()
    print("Welcome to the RPG App! Type 'exit' to quit or 'save' to manually save the game.")
    print("Use '+' at the end of a line to continue input on the next line.")
    print("Available commands: @save @exit @view_fields, @edit_field, @view_messages, @edit_message")

    display_recent_messages(app)
    while True:
        user_input = ""
        while True:
            line = input("You: " if not user_input else "... ")
            if line.endswith('+'):
                user_input += line[:-1] + "\n"
            else:
                user_input += line
                break

        response_generator, should_exit = app.process_input(user_input.strip(), True)

        if should_exit:
            break

        if isinstance(response_generator, str):
            print(f"Game Master: {response_generator}\n")
        else:
            print(f"Game Master:", end="", flush=True)
            for tok in response_generator:
                print(tok, end="", flush=True)
            print("\n")

class VirtualGameMasterConfig:
    def __init__(self):
        self.GAME_SAVE_FOLDER = os.getenv("GAME_SAVE_FOLDER")
        self.API_KEY = os.getenv("API_KEY")
        self.MODEL = os.getenv("MODEL")
        self.SYSTEM_MESSAGE_FILE = os.getenv("SYSTEM_MESSAGE_FILE")
        self.SAVE_SYSTEM_MESSAGE_FILE = os.getenv("SAVE_SYSTEM_MESSAGE_FILE")
        self.SAVE_REMINDER_MESSAGE_FILE = os.getenv("SAVE_REMINDER_MESSAGE_FILE")
        self.INITIAL_GAME_STATE = os.getenv("INITIAL_GAME_STATE")
        self.MAX_MESSAGES = int(os.getenv("MAX_MESSAGES"))
        self.KEPT_MESSAGES = int(os.getenv("KEPT_MESSAGES"))

# Usage
if __name__ == "__main__":
    config = VirtualGameMasterConfig()
    api_url = os.getenv("API_URL")
    config.GAME_SAVE_FOLDER = "NewDawnLlama/test2"
    api = OpenAIChatAPI(config.API_KEY, api_url, config.MODEL)
    api.settings.temperature = float(os.getenv("TEMPERATURE"))
    api.settings.top_p = float(os.getenv("TOP_P"))
    api.settings.top_k = int(os.getenv("TOP_K"))
    api.settings.min_p = float(os.getenv("MIN_P"))
    api.settings.tfs_z = float(os.getenv("TFS_Z"))
    app = VirtualGameMaster(config, api, True)
    run_cli(app)
