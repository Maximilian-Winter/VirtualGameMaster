import json
from abc import ABC, abstractmethod

import requests

from openai import OpenAI

from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.llm_output_settings import LlmStructuredOutputSettings, LlmStructuredOutputType
from llama_cpp_agent.providers import LlamaCppServerProvider, LlamaCppSamplingSettings
from llama_cpp_agent import MessagesFormatterType
from llama_cpp_agent.messages_formatter import get_predefined_messages_formatter, PromptMarkers, MessagesFormatter
from anthropic import Anthropic
from typing import List, Dict, Generator, Union


class ChatAPISettings(ABC):
    @abstractmethod
    def to_dict(self):
        pass


class ChatAPI(ABC):
    @abstractmethod
    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        pass

    @abstractmethod
    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        pass

    @abstractmethod
    def get_default_settings(self) -> ChatAPISettings:
        pass

    @abstractmethod
    def get_current_settings(self) -> ChatAPISettings:
        pass


class OpenAISettings(ChatAPISettings):
    def __init__(self):
        self.temperature = 0.4
        self.top_p = 1
        self.max_tokens = 1024

    def to_dict(self):
        return {
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens
        }


class OpenAIChatAPI(ChatAPI):

    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.settings = OpenAISettings()

    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            top_p=self.settings.top_p if settings is None else settings.top_p
        )
        return response.choices[0].message.content

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.settings.max_tokens,
            stream=True,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            top_p=self.settings.top_p if settings is None else settings.top_p
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def get_default_settings(self):
        return OpenAISettings()

    def get_current_settings(self):
        return self.settings


class OpenRouterSettings(ChatAPISettings):
    def __init__(self):
        self.temperature = 1.0
        self.top_p = 1.0
        self.top_k = 0
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0
        self.repetition_penalty = 1.0
        self.min_p = 0.0
        self.top_a = 0.0
        self.seed = None
        self.max_tokens = None

    def to_dict(self):
        return {
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'repetition_penalty': self.repetition_penalty,
            'min_p': self.min_p,
            'top_a': self.top_a,
            'seed': self.seed,
            'max_tokens': self.max_tokens
        }


class OpenRouterAPI(ChatAPI):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.settings = OpenRouterSettings()

    def _prepare_request_body(self, messages: List[Dict[str, str]], stream: bool = False, settings=None) -> Dict:
        body = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "stop": ["</s>", "[INST]", "[/INST]"],
            "temperature": self.settings.temperature if settings is None else settings.temperature,
            "top_p": self.settings.top_p if settings is None else settings.top_p,
            "top_k": self.settings.top_k if settings is None else settings.top_k,
            "frequency_penalty": self.settings.frequency_penalty if settings is None else settings.frequency_penalty,
            "presence_penalty": self.settings.presence_penalty if settings is None else settings.presence_penalty,
            "repetition_penalty": self.settings.repetition_penalty if settings is None else settings.repetition_penalty,
            "min_p": self.settings.min_p if settings is None else settings.min_p,
            "top_a": self.settings.top_a if settings is None else settings.top_a,
        }
        if self.settings.seed is not None or (settings is not None and settings.seed is not None):
            body["seed"] = self.settings.seed if settings is None else settings.seed
        if self.settings.max_tokens is not None or (settings is not None and settings.max_tokens is not None):
            body["max_tokens"] = self.settings.max_tokens if settings is None else settings.max_tokens
        return body

    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        response = requests.post(
            url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=self._prepare_request_body(messages, settings=settings)
        )
        return response.json()['choices'][0]['message']['content']

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        response = requests.post(
            url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            json=self._prepare_request_body(messages, stream=True, settings=settings),
            stream=True
        )

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data != '[DONE]':
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                content = chunk['choices'][0].get('delta', {}).get('content')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {data}")

    def get_default_settings(self):
        return OpenRouterSettings()

    def get_current_settings(self):
        return self.settings


class OpenRouterAPIPromptMode(ChatAPI):
    def __init__(self, api_key: str, model: str, messages_formatter_type: MessagesFormatterType = None):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.settings = OpenRouterSettings()
        if messages_formatter_type:
            self.main_message_formatter = get_predefined_messages_formatter(messages_formatter_type)
        else:
            prompt_markers = {
                Roles.system: PromptMarkers("""### Instructions:\n""", """\n\n"""),
                Roles.user: PromptMarkers("""### Player:\n""", """\n\n"""),
                Roles.assistant: PromptMarkers("""### Game Master:\n""", """\n\n"""),
                Roles.tool: PromptMarkers("""### Function Tool:\n""", """\n\n"""),
            }
            self.main_message_formatter = MessagesFormatter("", prompt_markers, False, ["### Player:"], False)

    def _prepare_request_body(self, messages: List[Dict[str, str]], stream: bool = False, settings=None) -> Dict:
        prompt, _ = self.main_message_formatter.format_conversation(messages, Roles.assistant)
        print(prompt)
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "stop": self.main_message_formatter.default_stop_sequences,
            "temperature": self.settings.temperature if settings is None else settings.temperature,
            "top_p": self.settings.top_p if settings is None else settings.top_p,
            "top_k": self.settings.top_k if settings is None else settings.top_k,
            "frequency_penalty": self.settings.frequency_penalty if settings is None else settings.frequency_penalty,
            "presence_penalty": self.settings.presence_penalty if settings is None else settings.presence_penalty,
            "repetition_penalty": self.settings.repetition_penalty if settings is None else settings.repetition_penalty,
            "min_p": self.settings.min_p if settings is None else settings.min_p,
            "top_a": self.settings.top_a if settings is None else settings.top_a,
        }
        if self.settings.seed is not None or (settings is not None and settings.seed is not None):
            body["seed"] = self.settings.seed if settings is None else settings.seed
        if self.settings.max_tokens is not None or (settings is not None and settings.max_tokens is not None):
            body["max_tokens"] = self.settings.max_tokens if settings is None else settings.max_tokens
        return body

    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        response = requests.post(
            url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=self._prepare_request_body(messages, settings=settings)
        )
        return response.json()['choices'][0]['text']

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        response = requests.post(
            url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            json=self._prepare_request_body(messages, stream=True, settings=settings),
            stream=True
        )

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data != '[DONE]':
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                content = chunk['choices'][0].get('text')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {data}")

    def get_default_settings(self):
        return OpenRouterSettings()

    def get_current_settings(self):
        return self.settings


class LlamaCppSettings(ChatAPISettings):
    """
    Settings for generating completions using the Llama.cpp server.

    Args:
        temperature (float): Controls the randomness of the generated completions. Higher values make the output more random.
        top_k (int): Controls the diversity of the top-k sampling. Higher values result in more diverse completions.
        top_p (float): Controls the diversity of the nucleus sampling. Higher values result in more diverse completions.
        min_p (float): Minimum probability for nucleus sampling. Lower values result in more focused completions.
        n_predict (int): Number of completions to predict. Set to -1 to use the default value.
        n_keep (int): Number of completions to keep. Set to 0 for all predictions.
        stream (bool): Enable streaming for long completions.
        additional_stop_sequences (List[str]): List of stop sequences to finish completion generation. The official stop sequences of the model get added automatically.
        tfs_z (float): Controls the temperature for top frequent sampling.
        typical_p (float): Typical probability for top frequent sampling.
        repeat_penalty (float): Penalty for repeating tokens in completions.
        repeat_last_n (int): Number of tokens to consider for repeat penalty.
        penalize_nl (bool): Enable penalizing newlines in completions.
        presence_penalty (float): Penalty for presence of certain tokens.
        frequency_penalty (float): Penalty based on token frequency.
        penalty_prompt (Union[None, str, List[int]]): Prompts to apply penalty for certain tokens.
        mirostat_mode (int): Mirostat level.
        mirostat_tau (float): Mirostat temperature.
        mirostat_eta (float): Mirostat eta parameter.
        seed (int): Seed for randomness. Set to -1 for no seed.
        ignore_eos (bool): Ignore end-of-sequence token.

    Attributes:
        temperature (float): Controls the randomness of the generated completions. Higher values make the output more random.
        top_k (int): Controls the diversity of the top-k sampling. Higher values result in more diverse completions.
        top_p (float): Controls the diversity of the nucleus sampling. Higher values result in more diverse completions.
        min_p (float): Minimum probability for nucleus sampling. Lower values result in more focused completions.
        n_predict (int): Number of completions to predict. Set to -1 to use the default value.
        n_keep (int): Number of completions to keep. Set to 0 for all predictions.
        stream (bool): Enable streaming for long completions.
        additional_stop_sequences (List[str]): List of stop sequences to finish completion generation. The official stop sequences of the model get added automatically.
        tfs_z (float): Controls the temperature for top frequent sampling.
        typical_p (float): Typical probability for top frequent sampling.
        repeat_penalty (float): Penalty for repeating tokens in completions.
        repeat_last_n (int): Number of tokens to consider for repeat penalty.
        penalize_nl (bool): Enable penalizing newlines in completions.
        presence_penalty (float): Penalty for presence of certain tokens.
        frequency_penalty (float): Penalty based on token frequency.
        penalty_prompt (Union[None, str, List[int]]): Prompts to apply penalty for certain tokens.
        mirostat_mode (int): Mirostat level.
        mirostat_tau (float): Mirostat temperature.
        mirostat_eta (float): Mirostat eta parameter.
        seed (int): Seed for randomness. Set to -1 for no seed.
        ignore_eos (bool): Ignore end-of-sequence token.
    Methods:
        save(file_path: str): Save the settings to a file.
        load_from_file(file_path: str) -> LlamaCppServerGenerationSettings: Load the settings from a file.
        load_from_dict(settings: dict) -> LlamaCppServerGenerationSettings: Load the settings from a dictionary.
        as_dict() -> dict: Convert the settings to a dictionary.

    """

    temperature: float = 0.8
    top_k: int = 40
    top_p: float = 0.95
    min_p: float = 0.05
    n_predict: int = -1
    n_keep: int = 0
    stream: bool = True
    additional_stop_sequences: List[str] = None
    tfs_z: float = 1.0
    typical_p: float = 1.0
    repeat_penalty: float = 1.1
    repeat_last_n: int = -1
    penalize_nl: bool = False
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    penalty_prompt: Union[None, str, List[int]] = None
    mirostat_mode: int = 0
    mirostat_tau: float = 5.0
    mirostat_eta: float = 0.1
    cache_prompt: bool = True
    seed: int = -1
    ignore_eos: bool = False
    samplers: List[str] = None

    def to_dict(self) -> dict:
        """
        Convert the settings to a dictionary.

        Returns:
            dict: The dictionary representation of the settings.
        """
        return {
            'temperature': self.temperature,
            'top_k': self.top_k,
            'top_p': self.top_p,
            'min_p': self.min_p,
            'n_predict': self.n_predict,
            'n_keep': self.n_keep,
            'stream': self.stream,
            'additional_stop_sequences': self.additional_stop_sequences,
            'tfs_z': self.tfs_z,
            'typical_p': self.typical_p,
            'repeat_penalty': self.repeat_penalty,
            'repeat_last_n': self.repeat_last_n,
            'penalize_nl': self.penalize_nl,
            'presence_penalty': self.presence_penalty,
            'frequency_penalty': self.frequency_penalty,
            'penalty_prompt': self.penalty_prompt,
            'mirostat_mode': self.mirostat_mode,
            'mirostat_tau': self.mirostat_tau,
            'mirostat_eta': self.mirostat_eta,
            'cache_prompt': self.cache_prompt,
            'seed': self.seed,
            'ignore_eos': self.ignore_eos,
            'samplers': self.samplers
        }


class LlamaAgentProvider(ChatAPI):

    def __init__(self, server_ip: str, api_key: str,
                 debug_output: bool = False):
        self.provider = LlamaCppServerProvider(server_ip, api_key=api_key)
        self.settings = LlamaCppSettings()

        self.debug_output = debug_output
        self.structured_settings = LlmStructuredOutputSettings(output_type=LlmStructuredOutputType.no_structured_output)

    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        self.settings.stream = False
        if settings is not None:
            settings.stream = False

        response = self.provider.create_chat_completion(messages, self.structured_settings,
                                                        LlamaCppSamplingSettings.load_from_dict(self.settings.to_dict()) if settings is None else LlamaCppSamplingSettings.load_from_dict(settings.to_dict()))
        return response['choices'][0][
            'message']['content']

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        self.settings.stream = True
        if settings is not None:
            settings.stream = True

        for tok in self.provider.create_chat_completion(messages, self.structured_settings,
                                                        self.settings if settings is None else settings):
            if "content" in tok['choices'][0]['delta']:
                text = tok['choices'][0]['delta']['content']
                yield text

    def get_default_settings(self):
        return LlamaCppSettings

    def get_current_settings(self):
        return self.settings


class LlamaAgentProviderCustom(ChatAPI):

    def __init__(self, server_ip: str, api_key: str, messages_formatter_type: MessagesFormatterType = None,
                 debug_output: bool = True):
        self.provider = LlamaCppServerProvider(server_ip, api_key=api_key)
        self.settings = self.provider.get_provider_default_settings()

        self.debug_output = debug_output
        messages_formatter_type = MessagesFormatterType.MISTRAL
        if messages_formatter_type:
            self.main_message_formatter = get_predefined_messages_formatter(messages_formatter_type)
        else:
            prompt_markers = {
                Roles.system: PromptMarkers("""### System Instructions:\n""", """\n\n"""),
                Roles.user: PromptMarkers("""### Player:\n""", """\n\n"""),
                Roles.assistant: PromptMarkers("""### Game Master:\n""", """\n\n"""),
                Roles.tool: PromptMarkers("""### Function Tool:\n""", """\n\n"""),
            }
            self.main_message_formatter = MessagesFormatter("", prompt_markers, False, ["### Player:"], False)

        self.structured_settings = LlmStructuredOutputSettings(output_type=LlmStructuredOutputType.no_structured_output)

    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        prompt, _ = self.main_message_formatter.format_conversation(messages=messages, response_role=Roles.assistant)
        self.settings.stream = False
        if settings is not None:
            settings.stream = False
        self.settings.additional_stop_sequences = self.main_message_formatter.default_stop_sequences
        if settings is not None:
            settings.additional_stop_sequences = self.main_message_formatter.default_stop_sequences
        if self.debug_output:
            print(prompt)
        response = self.provider.create_completion(prompt, self.structured_settings,
                                                   self.settings if settings is None else settings, "<s>")
        return response['choices'][0]['text']

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        prompt, _ = self.main_message_formatter.format_conversation(messages=messages, response_role=Roles.assistant)
        self.settings.stream = True
        if settings is not None:
            settings.stream = True
        self.settings.additional_stop_sequences = self.main_message_formatter.default_stop_sequences
        if settings is not None:
            settings.additional_stop_sequences = self.main_message_formatter.default_stop_sequences
        if self.debug_output:
            print(prompt)
        for tok in self.provider.create_completion(prompt, self.structured_settings,
                                                   self.settings if settings is None else settings, "<s>"):
            text = tok['choices'][0]['text']
            yield text

    def get_default_settings(self):
        return self.provider.get_provider_default_settings()

    def get_current_settings(self):
        return self.settings


class AnthropicSettings(ChatAPISettings):
    def __init__(self):
        self.temperature = 0.7
        self.top_p = 1.0
        self.max_tokens = 1024

    def to_dict(self):
        return {
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens
        }


class AnthropicChatAPI(ChatAPI):
    def __init__(self, api_key: str, model: str):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.settings = AnthropicSettings()

    def _prepare_messages(self, messages: List[Dict[str, str]]) -> tuple:
        system_message = None
        other_messages = []
        for message in messages:
            cleaned_message = {k: v for k, v in message.items() if k != 'id'}
            if cleaned_message['role'] == 'system':
                system_message = cleaned_message['content']
            else:
                other_messages.append(cleaned_message)
        return system_message, other_messages

    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        system, other_messages = self._prepare_messages(messages)
        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=other_messages,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            top_p=self.settings.top_p if settings is None else settings.top_p,
            max_tokens=self.settings.max_tokens if settings is None else settings.max_tokens
        )
        return response.content[0].text

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        system, other_messages = self._prepare_messages(messages)
        stream = self.client.messages.create(
            model=self.model,
            system=system,
            messages=other_messages,
            stream=True,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            top_p=self.settings.top_p if settings is None else settings.top_p,
            max_tokens=self.settings.max_tokens if settings is None else settings.max_tokens
        )
        for chunk in stream:
            if chunk.type == "content_block_delta":
                if chunk.delta.type == "text_delta":
                    yield chunk.delta.text

    def get_default_settings(self):
        return AnthropicSettings()

    def get_current_settings(self):
        return self.settings
