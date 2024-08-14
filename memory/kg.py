from VirtualGameMaster.memory.game_world_knowledge_graph import GameWorldKnowledgeGraph

game_world = GameWorldKnowledgeGraph.load("game_world_anthropic.json")

game_world.knowledge_graph.visualize("output", "png")