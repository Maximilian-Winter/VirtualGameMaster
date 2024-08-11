import json

from pydantic import BaseModel, Field

from ToolAgents import ToolRegistry, FunctionTool
from ToolAgents.agents import MistralAgent, HostedToolAgent
from ToolAgents.agents.mistral_agent_parts import MistralToolCallHandler
from ToolAgents.interfaces import HostedLLMProvider
from ToolAgents.interfaces.llm_tokenizer import HuggingFaceTokenizer
from ToolAgents.provider import LlamaCppServerProvider
from ToolAgents.provider import VLLMServerProvider
from ToolAgents.utilities import ChatHistory
from VirtualGameMaster.memory.game_world_knowledge_graph import GameWorldKnowledgeGraph


class MistralAltAgent(HostedToolAgent):
    def __init__(self, provider: HostedLLMProvider, tokenizer_file: str = "NousResearch/Hermes-2-Pro-Llama-3-8B", debug_output: bool = False):
        super().__init__(provider, HuggingFaceTokenizer(tokenizer_file), MistralToolCallHandler(debug_output),
                         debug_output)


# provider = VLLMServerProvider("http://localhost:8000/v1", api_key="token-abc123", model="solidrust/Mistral-7B-Instruct-v0.3-AWQ", huggingface_model="solidrust/Mistral-7B-Instruct-v0.3-AWQ")
provider = LlamaCppServerProvider("http://127.0.0.1:8080/")
agent = MistralAltAgent(provider=provider, debug_output=True)

settings = provider.get_default_settings()
settings.neutralize_all_samplers()

settings.temperature = 0.3

settings.set_max_new_tokens(4096)

game_knowledge_graph = GameWorldKnowledgeGraph()
tools = game_knowledge_graph.get_single_tools()


class send_message(BaseModel):
    """
    Sends a message to the user.
    """

    content: str = Field(..., description="Content of the message to be sent.")

    def run(self):
        print(self.content)
        return "Message sent."


tools.append(FunctionTool(send_message))

chat_history = ChatHistory()
chat_history.add_system_message(f"""Your task is to generate a world for a pen and paper game and save it to a knowledge graph.

You have access to the following functions to add information to the world knowledge graph:

{'\n\n'.join([tool.get_text_documentation() for tool in tools])}

Always remember to wait for you tool call responses after creating entities before adding relationships with them. You need the entity ids that are part of the tool call responses to add relationships!!!!
""")
chat_history.add_user_message(
    "Generate a detailed game world with many entities and relationships, based on the Sword Coast and Waterdeep!")

tool_registry = ToolRegistry(guided_sampling_enabled=False)

tool_registry.add_tools(tools=tools)

result = agent.get_streaming_response(
    messages=chat_history.to_list(),
    sampling_settings=settings, tool_registry=tool_registry)
res = None
for tok in result:
    print(tok, end="", flush=True)
print()
chat_history.add_list_of_dicts(agent.last_messages_buffer)
chat_history.save_history("./test_chat_history_after_mistral.json")
game_knowledge_graph.save("game_world.json")

while True:
    user_input = input("> ")
    if user_input == "exit":
        break
    chat_history.add_user_message(user_input)
    result = agent.get_streaming_response(
        messages=chat_history.to_list(),
        sampling_settings=settings, tool_registry=tool_registry)
    res = None
    for tok in result:
        print(tok, end="", flush=True)
    print()
    chat_history.add_list_of_dicts(agent.last_messages_buffer)
    chat_history.save_history("./test_chat_history_after_mistral.json")
    game_knowledge_graph.save("game_world.json")
chat_history.add_list_of_dicts(agent.last_messages_buffer)
chat_history.save_history("./test_chat_history_after_mistral.json")
game_knowledge_graph.save("game_world.json")
