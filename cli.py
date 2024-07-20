from virtual_game_master import VirtualGameMasterConfig, VirtualGameMaster, VirtualGameMasterChatAPISelector


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

        print(f"\n\n", flush=True)
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
    api_selector = VirtualGameMasterChatAPISelector(config)
    api = api_selector.get_api()
    app = VirtualGameMaster(config, api, True)
    run_cli(app)
