from chat_api import ChatAPI, OpenAIChatAPI, OpenRouterAPI, OpenRouterAPIPromptMode, LlamaAgentProvider, \
    LlamaAgentProviderCustom, AnthropicChatAPI, MistralChatAPI, GroqChatAPI
from virtual_game_master import VirtualGameMasterConfig


class VirtualGameMasterChatAPISelector:
    def __init__(self, config: VirtualGameMasterConfig):
        self.config = config

    def get_api(self) -> ChatAPI:
        if self.config.API_TYPE == "openai":
            api = OpenAIChatAPI(self.config.API_KEY, self.config.API_URL, self.config.MODEL)
        elif self.config.API_TYPE == "openrouter":
            api = OpenRouterAPI(self.config.API_KEY, self.config.MODEL)
        elif self.config.API_TYPE == "openrouter_custom":
            api = OpenRouterAPIPromptMode(self.config.API_KEY, self.config.MODEL)
        elif self.config.API_TYPE == "llamacpp":
            api = LlamaAgentProvider(self.config.API_URL, self.config.API_KEY)
        elif self.config.API_TYPE == "llamacpp_custom":
            api = LlamaAgentProviderCustom(self.config.API_URL, self.config.API_KEY)
        elif self.config.API_TYPE == "anthropic":
            api = AnthropicChatAPI(self.config.API_KEY, self.config.MODEL)
        elif self.config.API_TYPE == "groq":
            api = GroqChatAPI(self.config.API_KEY, self.config.MODEL)
        elif self.config.API_TYPE == "mistral":  # Add the new condition for Mistral
            api = MistralChatAPI(self.config.API_KEY, self.config.MODEL)
        else:
            raise ValueError(f"Unsupported API type: {self.config.API_TYPE}")

        # Set common settings
        api.settings.temperature = self.config.TEMPERATURE
        api.settings.top_p = self.config.TOP_P
        api.settings.max_tokens = self.config.MAX_TOKENS

        # Set additional settings for specific APIs
        if self.config.API_TYPE in ["openrouter", "openrouter_custom", "llamacpp", "llamacpp_custom"]:
            api.settings.top_k = self.config.TOP_K
            api.settings.min_p = self.config.MIN_P

        if self.config.API_TYPE in ["llamacpp", "llamacpp_custom"]:
            api.settings.tfs_z = self.config.TFS_Z

        return api
