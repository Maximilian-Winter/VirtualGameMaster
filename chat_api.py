import json
from abc import ABC, abstractmethod

import requests
from groq import Groq
from mistral_common.protocol.instruct.messages import ChatMessage

from openai import OpenAI

from ToolAgents import FunctionTool
from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.llm_output_settings import LlmStructuredOutputSettings, LlmStructuredOutputType
from llama_cpp_agent.providers import LlamaCppServerProvider, LlamaCppSamplingSettings
from llama_cpp_agent import MessagesFormatterType
from llama_cpp_agent.messages_formatter import get_predefined_messages_formatter, PromptMarkers, MessagesFormatter
from anthropic import Anthropic
from typing import Union, Optional, Any

from mistralai.client import MistralClient


from typing import List, Dict, Generator


def clean_history_messages(history_messages: List[dict]) -> List[dict]:
    clean_messages = []
    for msg in history_messages:
        if "id" in msg:
            msg.pop("id")
        clean_messages.append(msg)

    return clean_messages


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
            messages=clean_history_messages(messages),
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            top_p=self.settings.top_p if settings is None else settings.top_p
        )
        return response.choices[0].message.content

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=clean_history_messages(messages),
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
        self.stop = []

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
            'max_tokens': self.max_tokens,
            'stop': self.stop
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
            "messages": clean_history_messages(messages),
            "stream": stream,
            "stop": self.settings.stop if settings is None else settings.stop,
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
    temperature: float = 0.3
    top_k: int = 0
    top_p: float = 1.0
    min_p: float = 0.0
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

        response = self.provider.create_chat_completion(clean_history_messages(messages), self.structured_settings,
                                                        LlamaCppSamplingSettings.load_from_dict(
                                                            self.settings.to_dict()) if settings is None else LlamaCppSamplingSettings.load_from_dict(
                                                            settings.to_dict()))
        return response['choices'][0][
            'message']['content']

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        self.settings.stream = True
        if settings is not None:
            settings.stream = True

        for tok in self.provider.create_chat_completion(clean_history_messages(messages), self.structured_settings,
                                                        LlamaCppSamplingSettings.load_from_dict(
                                                            self.settings.to_dict()) if settings is None else LlamaCppSamplingSettings.load_from_dict(
                                                            settings.to_dict())):
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
        self.top_k = 0.0
        self.max_tokens = 1024
        self.stop_sequences = []
        self.cache_system_prompt = True
        self.cache_user_messages = False
        self.cache_recent_messages = 10

    def to_dict(self):
        return {
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'max_tokens': self.max_tokens,
            'stop_sequences': self.stop_sequences,
            'cache_system_prompt': self.cache_system_prompt,
            'cache_user_messages': self.cache_user_messages,
            'cache_recent_messages': self.cache_recent_messages
        }


class AnthropicChatAPI(ChatAPI):
    def __init__(self, api_key: str, model: str):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.settings = AnthropicSettings()

    def prepare_messages(self, settings: AnthropicSettings, messages: List[Dict[str, str]]) -> tuple:
        system_message = None
        other_messages = []
        cleaned_messages = clean_history_messages(messages)
        for i, message in enumerate(cleaned_messages):
            if message['role'] == 'system':
                system_message = [
                    {"type": "text", "text": message['content']}
                ]
                if settings.cache_system_prompt:
                    system_message[0]["cache_control"] = {"type": "ephemeral"}
            else:
                msg = {
                    'role': message['role'],
                    'content': [
                        {
                            "type": "text",
                            "text": message["content"]
                        }
                    ],
                }
                if settings.cache_user_messages:
                    if i >= len(cleaned_messages) - settings.cache_recent_messages:
                        msg["content"][0]["cache_control"] = {"type": "ephemeral"}

                other_messages.append(msg)
        return system_message, other_messages

    def get_response(self, messages: List[Dict[str, str]], settings=None,
                     tools: Optional[List[FunctionTool]] = None) -> str:
        system, other_messages = self.prepare_messages(self.settings if settings is None else settings, messages)
        anthropic_tools = [tool.to_anthropic_tool() for tool in tools] if tools else None
        response = self.client.messages.create(
            extra_headers={
                "anthropic-beta": "prompt-caching-2024-07-31"
            } if self.settings.cache_system_prompt or (settings is not None and settings.cache_system_prompt) else None,
            model=self.model,
            system=system if system else [],
            messages=other_messages,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            top_p=self.settings.top_p if settings is None else settings.top_p,
            top_k=self.settings.top_k if settings is None else settings.top_k,
            max_tokens=self.settings.max_tokens if settings is None else settings.max_tokens,
            stop_sequences=self.settings.stop_sequences if settings is None else settings.stop_sequences,
            tools=anthropic_tools
        )
        if tools and (response.content[0].type == 'tool_use' or (
                len(response.content) > 1 and response.content[1].type == 'tool_use')):
            if response.content[0].type == 'tool_use':
                return json.dumps({
                    "content": None,
                    "tool_calls": [{
                        "function": {
                            "id": response.content[0].id,
                            "name": response.content[0].name,
                            "arguments": response.content[0].input
                        }
                    }]
                })
            elif response.content[1].type == 'tool_use':
                return json.dumps({
                    "content": response.content[0].text,
                    "tool_calls": [{
                        "function": {
                            "id": response.content[1].id,
                            "name": response.content[1].name,
                            "arguments": response.content[1].input
                        }
                    }]
                })
        return response.content[0].text

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None,
                               tools: Optional[List[FunctionTool]] = None) -> Generator[str, None, None]:
        system, other_messages = self.prepare_messages(self.settings if settings is None else settings, messages)
        anthropic_tools = [tool.to_anthropic_tool() for tool in tools] if tools else None

        stream = self.client.messages.create(
            extra_headers={
                "anthropic-beta": "prompt-caching-2024-07-31"
            } if self.settings.cache_system_prompt or (settings is not None and settings.cache_system_prompt) else None,
            model=self.model,
            system=system if system else [],
            messages=other_messages,
            stream=True,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            top_p=self.settings.top_p if settings is None else settings.top_p,
            max_tokens=self.settings.max_tokens if settings is None else settings.max_tokens,
            tools=anthropic_tools if anthropic_tools else []
        )

        current_tool_call = None
        content = ""
        for chunk in stream:
            if chunk.type == "content_block_start":
                if chunk.content_block.type == "tool_use":
                    current_tool_call = {
                        "function": {
                            "id": chunk.content_block.id,
                            "name": chunk.content_block.name,
                            "arguments": ""
                        }
                    }
            elif chunk.type == "content_block_delta":
                if chunk.delta.type == "text_delta":
                    content += chunk.delta.text
                    yield chunk.delta.text
                elif chunk.delta.type == "input_json_delta":
                    if current_tool_call:
                        current_tool_call["function"]["arguments"] += chunk.delta.partial_json

            elif chunk.type == "content_block_stop":
                if current_tool_call:
                    yield json.dumps({
                        "content": content if len(content) > 0 else None,
                        "tool_calls": [current_tool_call]
                    })
                    current_tool_call = None

    def generate_tool_use_message(self, content: str, tool_call_id: str, tool_name: str, tool_args: str) -> Dict[
        str, Any]:
        if content is None or len(content) == 0:
            return {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": tool_call_id,
                        "name": tool_name,
                        "input": json.loads(tool_args) if isinstance(tool_args, str) else tool_args
                    }
                ]
            }
        else:
            return {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": content
                    },
                    {
                        "type": "tool_use",
                        "id": tool_call_id,
                        "name": tool_name,
                        "input": json.loads(tool_args) if isinstance(tool_args, str) else tool_args
                    }
                ]
            }

    def generate_tool_response_message(self, tool_call_id: str, tool_name: str, tool_response: str) -> Dict[str, Any]:
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call_id,
                    "content": tool_response
                }
            ]
        }

    def get_default_settings(self):
        return AnthropicSettings()

    def get_current_settings(self):
        return self.settings


class GroqSettings(ChatAPISettings):
    def __init__(self):
        self.temperature = 0.5
        self.max_tokens = 1024
        self.top_p = 1
        self.stop = None

    def to_dict(self):
        return {
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'stop': self.stop
        }


class GroqChatAPI(ChatAPI):
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.settings = GroqSettings()

    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=clean_history_messages(messages),
            model=self.model,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            max_tokens=self.settings.max_tokens if settings is None else settings.max_tokens,
            top_p=self.settings.top_p if settings is None else settings.top_p,
            stop=self.settings.stop if settings is None else settings.stop,
            stream=False
        )
        return chat_completion.choices[0].message.content

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        stream = self.client.chat.completions.create(
            messages=clean_history_messages(messages),
            model=self.model,
            temperature=self.settings.temperature if settings is None else settings.temperature,
            max_tokens=self.settings.max_tokens if settings is None else settings.max_tokens,
            top_p=self.settings.top_p if settings is None else settings.top_p,
            stop=self.settings.stop if settings is None else settings.stop,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def get_default_settings(self):
        return GroqSettings()

    def get_current_settings(self):
        return self.settings


class MistralSettings(ChatAPISettings):
    def __init__(self):
        self.temperature = 0.7
        self.max_tokens = 1024
        self.top_p = 1.0

    def to_dict(self):
        return {
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p
        }


class MistralChatAPI(ChatAPI):
    def __init__(self, api_key: str, model: str):
        self.client = MistralClient(api_key=api_key)
        self.model = model
        self.settings = MistralSettings()

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[ChatMessage]:
        return [ChatMessage(role=msg['role'], content=msg['content']) for msg in messages]

    def get_response(self, messages: List[Dict[str, str]], settings=None) -> str:
        chat_response = self.client.chat(
            model=self.model,
            messages=self._convert_messages(messages),
            temperature=self.settings.temperature if settings is None else settings.temperature,
            max_tokens=self.settings.max_tokens if settings is None else settings.max_tokens,
            top_p=self.settings.top_p if settings is None else settings.top_p
        )
        return chat_response.choices[0].message.content

    def get_streaming_response(self, messages: List[Dict[str, str]], settings=None) -> Generator[str, None, None]:
        stream_response = self.client.chat_stream(
            model=self.model,
            messages=self._convert_messages(messages),
            temperature=self.settings.temperature if settings is None else settings.temperature,
            max_tokens=self.settings.max_tokens if settings is None else settings.max_tokens,
            top_p=self.settings.top_p if settings is None else settings.top_p
        )
        for chunk in stream_response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def get_default_settings(self):
        return MistralSettings()

    def get_current_settings(self):
        return self.settings
