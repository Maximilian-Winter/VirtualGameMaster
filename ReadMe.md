# Virtual Game Master

Virtual Game Master is an innovative application that uses large language models to act as a game master for role-playing games. It provides both a command-line interface (CLI) and a web-based user interface for interacting with the virtual game master.

## Features

- AI-powered game master using large language models
- Supports llama.cpp server, Openrouter API, OpenAI-compatible APIs, Anthropic API, Groq API and MistralAI API
- Command-line interface for text-based interaction
- Web-based user interface for a more visual experience
- Customizable game settings and scenarios
- Save and load game states
- Extensible command system

## Prerequisites

- Python 3.7+
- Node.js and npm (for the web UI)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Maximilian-Winter/VirtualGameMaster.git
   cd virtual-game-master
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
    - Copy the `.env.example` file to `.env`
    - Edit the `.env` file to add your API keys and customize settings

4. (Optional) For the web UI, install Node.js dependencies:
   ```
   cd virtual-game-master-webui
   npm install
   ```

## Setting up the .env file

The `.env` file is crucial for configuring your Virtual Game Master. Follow these steps to set it up correctly:

1. In the root directory of the project, copy the `.env.example` file and rename it to `.env`:
   ```
   cp .env.example .env
   ```

2. Open the `.env` file in a text editor.

3. Configure the following settings:

   a. Game Save Folder:
   ```
   GAME_SAVE_FOLDER=chat_history/your_game_name
   ```
   Replace `your_game_name` with a name for your game save folder.

   b. Initial Game State:
   ```
   INITIAL_GAME_STATE=game_starters/rpg_new.yaml
   ```
   You can use `game_starters/rpg_new.yaml` for a blank template, or look into `game_starters` for a pre-configured game worlds.

   c. Message Limits:
   ```
   MAX_MESSAGES=20
   KEPT_MESSAGES=10
   ```
   Adjust these values as needed. `MAX_MESSAGES` is the maximum number of messages in the chat history before creating an updated game state. `KEPT_MESSAGES` is the number of recent messages to keep after updating the game state.

   d. System Messages:
   ```
   SYSTEM_MESSAGE_FILE=prompts/system_message.txt
   SAVE_SYSTEM_MESSAGE_FILE=prompts/alt_save_system_message.txt
   ```
   These files contain instructions for the AI. You can modify them to change the AI's behavior.

   e. Command Prefix:
   ```
   COMMAND_PREFIX=/
   ```
   This is the symbol used to denote commands in the chat interface.

   f. API Configuration:
   ```
   API_TYPE=openai
   API_KEY=sk-your_api_key_here
   API_URL=https://api.openai.com/v1
   MODEL=gpt-3.5-turbo
   ```
    - Set `API_TYPE` to your chosen provider (openai, openrouter, llamacpp, anthropic, or groq).
    - Replace `sk-your_api_key_here` with your actual API key.
    - Adjust `API_URL` if you're using a different API endpoint.
    - Set `MODEL` to the specific model you want to use.

   g. Response Settings:
   ```
   MAX_TOKENS_PER_RESPONSE=4096
   TEMPERATURE=0.7
   TOP_P=1.0
   TOP_K=0
   MIN_P=0.00
   TFS_Z=1.0
   ```
   These settings control the AI's responses. Adjust them to fine-tune the AI's behavior.

4. Save the `.env` file after making your changes.

Remember to never commit your `.env` file to version control, as it contains sensitive information like API keys.

## Usage

### Command-Line Interface

To start the CLI version of the Virtual Game Master:

```
python cli.py
```

Use the following commands within the CLI:

- Type your messages to interact with the game master
- Use `+` at the end of a line to continue input on the next line
- Use the command prefix (default: `/`) to execute special commands:
    - `/help`: Display all available commands
    - `/exit`: Save the game and exit
    - `/save`: Manually save the current game state
    - `/view_fields`: Display all template fields and their current values
    - `/edit_field <field_name> <new_value>`: Edit a specific template field
    - `/view_messages [count]`: Display the last N messages in the chat history
    - `/edit_message <message_id> <new_content>`: Edit a specific message
    - `/delete_last <count>`: Delete the last N messages from the chat history
    - `/rm_all`: Delete all messages from the chat history
    - `/show_history`: Display the current chat history
    - `/show_history_full`: Display the complete chat history

### Web User Interface

To start the web server:

```
python fast_api_backend.py
```

To start the React development server:

```
cd virtual-game-master-webui
npm start
```

Then open your web browser and navigate to `http://localhost:3000` to access the web UI.

The web UI provides a more visual and interactive way to engage with the virtual game master. You can:

- Send messages to the game master
- View and edit the chat history
- Manage template fields
- Save and load game states

## Customization

- Modify the `rpg_new.yaml` file to create custom game scenarios
- Edit the system messages in the `prompts` folder to adjust the game master's behavior
- Extend the `CommandSystem` in `command_system.py` to add new commands

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for the GPT models
- FastAPI for the backend framework
- React for the frontend framework