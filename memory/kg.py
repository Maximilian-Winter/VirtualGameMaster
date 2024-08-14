from VirtualGameMaster.memory.game_world_knowledge_graph import GameWorldKnowledgeGraph

game_world = GameWorldKnowledgeGraph()

game_world.load_game("game_world42_anthropic42.json")

game_world.knowledge_graph.visualize("output4222", "png")