from ToolAgents.agents import MistralAgent
from ToolAgents.provider import LlamaCppServerProvider
from ToolAgents.utilities import ChatHistory
from VirtualGameMaster.memory.game_world_knowledge_graph import GameWorldKnowledgeGraph, CharacterType, Character, CharacterQuery, BeastType, Beast, BeastQuery, LocationType, Location, LocationQuery, ItemType, Item, ItemQuery, FactionType, Faction, FactionQuery, QuestType, Quest, QuestQuery, EventType, Event, EventQuery
from code_executer import PythonCodeExecutor, system_message_code_agent, run_code_agent

provider = LlamaCppServerProvider("http://127.0.0.1:8080/")

agent = MistralAgent(provider=provider, debug_output=True)

settings = provider.get_default_settings()
settings.neutralize_all_samplers()
settings.temperature = 0.3
settings.set_stop_tokens(["</s>"], None)
settings.set_max_new_tokens(4096)

game_world = GameWorldKnowledgeGraph()
tools = game_world.get_unified_tools()

chat_history = ChatHistory()
chat_history.add_system_message("<system_instructions>\n" + system_message_code_agent + f"""\n\nYour task is to generate a world for a pen and paper game and save it to a knowledge graph.

You have access to the following predefined types and functions to add information to the world knowledge graph:

```python
{'\n\n'.join([tool.get_python_documentation() for tool in tools])}
```

You can use these predefined types and call these predefined functions in Python like in this example:

```python_interpreter
example_object = ExampleClass(a="a", b=10, c="c")
return_value = example_function(example_argument=example_object)
```

Always remember to save the return value in a variable, when you add an entity. You need the entity ids that are in the return value of the add_entity function to add relationships!!!!
""" + "\n</system_instructions>")
python_code_executor = PythonCodeExecutor(
    tools=tools, predefined_classes=[CharacterType, Character, CharacterQuery, BeastType, Beast, BeastQuery, LocationType, Location, LocationQuery, ItemType, Item, ItemQuery, FactionType, Faction, FactionQuery, QuestType, Quest, QuestQuery, EventType, Event, EventQuery])

prompt = "Generate a detailed game world with many entities and relationships, based on the Sword Coast and Waterdeep!"

run_code_agent(agent=agent, settings=settings, chat_history=chat_history, user_input=prompt,
               python_code_executor=python_code_executor)

chat_history.save_history("./test_chat_history_after_mistral.json")
