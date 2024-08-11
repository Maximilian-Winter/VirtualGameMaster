import json

from ToolAgents.agents import MistralAgent
from ToolAgents.provider import LlamaCppServerProvider
from ToolAgents.provider import VLLMServerProvider
from ToolAgents.utilities import ChatHistory
from VirtualGameMaster.memory.game_world_knowledge_graph import GameWorldKnowledgeGraph

# provider = VLLMServerProvider("http://localhost:8000/v1", api_key="token-abc123", model="solidrust/Mistral-7B-Instruct-v0.3-AWQ", huggingface_model="solidrust/Mistral-7B-Instruct-v0.3-AWQ")
provider = LlamaCppServerProvider("http://127.0.0.1:8080/")
agent = MistralAgent(provider=provider, debug_output=False)

settings = provider.get_default_settings()
settings.neutralize_all_samplers()

settings.temperature = 0.3

settings.set_max_new_tokens(4096)

game_knowledge_graph = GameWorldKnowledgeGraph()
tools = game_knowledge_graph.get_unified_tools()

[print(tool.get_text_documentation()) for tool in tools]

chat_history = ChatHistory()
chat_history.add_user_message("Hello World!")


result = agent.get_streaming_response(
    messages=chat_history.to_list(),
    sampling_settings=settings, tools=tools)
res = None
for tok in result:
    print(tok, end="", flush=True)
print()


chat_history.add_list_of_dicts(agent.last_messages_buffer)
chat_history.save_history("./test_chat_history_after_mistral.json")
