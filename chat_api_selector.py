from chat_api import ChatAPI, OpenAIChatAPI, OpenRouterAPI, OpenRouterAPIPromptMode, LlamaAgentProvider, LlamaAgentProviderCustom, AnthropicChatAPI, GroqChatAPI

from virtual_game_master import VirtualGameMasterConfig

class VirtualGameMasterChatAPISelector:
    def __init__(self, config: VirtualGameMasterConfig):
        self.config = config

    def get_api(self) -> ChatAPI:
        if self.config.API_TYPE == "openai":
            api = OpenAIChatAPI(self.config.API_KEY, self.config.API_URL, self.config.MODEL)
            api.settings.temperature = self.config.TEMPERATURE
            api.settings.top_p = self.config.TOP_P
            api.settings.max_tokens = self.config.MAX_TOKENS
            return api
        elif self.config.API_TYPE == "openrouter":
            api = OpenRouterAPI(self.config.API_KEY, self.config.MODEL)
            api.settings.temperature = self.config.TEMPERATURE
            api.settings.top_p = self.config.TOP_P
            api.settings.top_k = self.config.TOP_K
            api.settings.min_p = self.config.MIN_P
            api.settings.max_tokens = self.config.MAX_TOKENS
            return api
        elif self.config.API_TYPE == "openrouter_custom":
            api = OpenRouterAPIPromptMode(self.config.API_KEY, self.config.MODEL)
            api.settings.temperature = self.config.TEMPERATURE
            api.settings.top_p = self.config.TOP_P
            api.settings.top_k = self.config.TOP_K
            api.settings.min_p = self.config.MIN_P
            api.settings.max_tokens = self.config.MAX_TOKENS
            return api
        elif self.config.API_TYPE == "llamacpp":
            api = LlamaAgentProvider(self.config.API_URL, self.config.API_KEY)
            api.settings.temperature = self.config.TEMPERATURE
            api.settings.top_p = self.config.TOP_P
            api.settings.top_k = self.config.TOP_K
            api.settings.min_p = self.config.MIN_P
            api.settings.tfs_z = self.config.TFS_Z
            api.settings.max_tokens = self.config.MAX_TOKENS
            return api
        elif self.config.API_TYPE == "llamacpp_custom":
            api = LlamaAgentProviderCustom(self.config.API_URL, self.config.API_KEY)
            api.settings.temperature = self.config.TEMPERATURE
            api.settings.top_p = self.config.TOP_P
            api.settings.top_k = self.config.TOP_K
            api.settings.min_p = self.config.MIN_P
            api.settings.tfs_z = self.config.TFS_Z
            api.settings.max_tokens = self.config.MAX_TOKENS
            return api
        elif self.config.API_TYPE == "anthropic":
            api = AnthropicChatAPI(self.config.API_KEY, self.config.MODEL)
            api.settings.temperature = self.config.TEMPERATURE
            api.settings.top_p = self.config.TOP_P
            api.settings.max_tokens = self.config.MAX_TOKENS
            return api
        elif self.config.API_TYPE == "groq":  # Add the new condition for Groq
            api = GroqChatAPI(self.config.API_KEY, self.config.MODEL)
            api.settings.temperature = self.config.TEMPERATURE
            api.settings.top_p = self.config.TOP_P
            api.settings.max_tokens = self.config.MAX_TOKENS
            return api
        else:
            raise ValueError(f"Unsupported API type: {self.config.API_TYPE}")