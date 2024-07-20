# Virtual Game Master

Virtual Game Master is an open-source project that leverages Large Language Models (LLMs) to create an interactive and dynamic role-playing game experience. This system supports various LLM backends, including OpenAI-compatible APIs, Open Router, and locally hosted llama.cpp server.

## Features

- Support for multiple LLM backends:
    - OpenAI-compatible APIs
    - Open Router
    - Local llama.cpp server
- Command-line interface for basic interaction
- React-based web user interface for enhanced gameplay
- Automatic game state saving through LLM-generated summaries
- Flexible scenario support with YAML-based game configurations
- Easy switching between different LLM backends

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js and npm (for the React web UI)
- Access to an LLM API or a local llama.cpp server

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/virtual-game-master.git
   cd virtual-game-master
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Copy the `.env.example` file to `.env` and modify it with your settings:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file with your preferred text editor and add your API keys and configuration.

4. (Optional) For the web UI, install JavaScript dependencies:
   ```
   cd virtual-game-master-webui
   npm install
   ```

### Configuration

The `.env` file contains important configuration settings for the Virtual Game Master. Here's an explanation of key settings:

- `API_TYPE`: Choose between "openai", "openrouter", or "llamacpp"
- `API_KEY`: Your API key for the chosen service
- `API_URL`: The endpoint URL for the API (including the llama.cpp server address)
- `MODEL`: The specific model to use
- `TEMPERATURE`, `TOP_P`, `TOP_K`, `MIN_P`, `TFS_Z`: Model parameters

Adjust these settings according to your chosen LLM backend and preferences.

### Usage

#### Command-line Interface

Run the CLI application:
```
python cli.py
```

#### Web User Interface

1. Start the backend server:
   ```
   python fast_api_backend.py
   ```

2. In a new terminal, start the React development server:
   ```
   cd virtual-game-master-webui
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000` to access the web UI.

## Creating Custom Scenarios

Custom scenarios can be created using YAML files. Place your scenario YAML files in the `game_starters` directory. Refer to the existing `rpg_elysia.yaml` file as a template for creating your own scenarios.

## Automatic Game State Saving

The Virtual Game Master automatically saves the game state at regular intervals by instructing the LLM to write down the current status. This feature ensures that progress is not lost and allows for easy resumption of gameplay. The frequency of saves is determined by the `MAX_MESSAGES` setting in the `.env` file.

## Switching Between LLM Backends

To switch between different LLM backends:

1. Open your `.env` file
2. Change the `API_TYPE` to either "openai", "openrouter", or "llamacpp"
3. Update the `API_URL` and `API_KEY` accordingly
4. Adjust any model-specific parameters as needed

The `LLMChatAPISelector` class will automatically use the correct API based on these settings.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for their GPT models and API
- The llama.cpp project for enabling local LLM hosting
- OpenRouter for providing access to various LLM models
- All contributors and users of this project

## Troubleshooting

If you encounter any issues:

1. Ensure all environment variables in the `.env` file are correctly set.
2. Verify that your API key is valid and has the necessary permissions.
3. If using a local llama.cpp server, ensure it's running and accessible at the specified URL.
4. Check that you have the correct dependencies installed for your chosen API type.

For more specific issues, please open an issue on the GitHub repository.