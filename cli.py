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


# Usage
if __name__ == "__main__":
    config = VirtualGameMasterConfig()
    config.GAME_SAVE_FOLDER = "chat_history/new_game"
    api = OpenAIChatAPI(config.API_KEY, config.API_URL, config.MODEL)
    api.settings.temperature = config.TEMPERATURE
    api.settings.top_p = config.TOP_P
    # Not available when using OpenAI client
    # api.settings.top_k = config.TOP_K
    # api.settings.min_p = config.MIN_P
    # api.settings.tfs_z = config.TFS_Z
    app = VirtualGameMaster(config, api, False)
    run_cli(app)
