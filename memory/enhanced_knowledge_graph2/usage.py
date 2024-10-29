from enhanced_knowledge_graph import KnowledgeGraph, Entity, EntityQuery

# Initialize the knowledge graph
kg = KnowledgeGraph()

# Create movie entities
inception = Entity(
    entity_type="Movie",
    attributes={
        "title": "Inception",
        "year": 2010,
        "genre": "Sci-Fi",
        "rating": 8.8
    }
)
inception_id = kg.add_entity(inception)

dark_knight = Entity(
    entity_type="Movie",
    attributes={
        "title": "The Dark Knight",
        "year": 2008,
        "genre": "Action",
        "rating": 9.0
    }
)
dark_knight_id = kg.add_entity(dark_knight)

# Create director entity
nolan = Entity(
    entity_type="Director",
    attributes={
        "name": "Christopher Nolan",
        "birth_year": 1970,
        "nationality": "British-American"
    }
)
nolan_id = kg.add_entity(nolan)

# Create actor entities
leo = Entity(
    entity_type="Actor",
    attributes={
        "name": "Leonardo DiCaprio",
        "birth_year": 1974,
        "nationality": "American"
    }
)
leo_id = kg.add_entity(leo)

bale = Entity(
    entity_type="Actor",
    attributes={
        "name": "Christian Bale",
        "birth_year": 1974,
        "nationality": "British"
    }
)
bale_id = kg.add_entity(bale)

# Add relationships
kg.add_relationship(
    inception_id,
    "DIRECTED_BY",
    nolan_id,
    attributes={"year": 2010}
)

kg.add_relationship(
    dark_knight_id,
    "DIRECTED_BY",
    nolan_id,
    attributes={"year": 2008}
)

kg.add_relationship(
    inception_id,
    "STARS",
    leo_id,
    attributes={"role": "Cobb"}
)

kg.add_relationship(
    dark_knight_id,
    "STARS",
    bale_id,
    attributes={"role": "Batman"}
)

# Demonstrate various queries and analyses

# 1. Query all movies
print("\nQuerying all movies:")
movie_query = EntityQuery(entity_type="Movie")
print(kg.query_entities(movie_query))

# 2. Find relationships for Inception
print("\nRelationships for Inception:")
print(kg.query_relationships(inception_id))

# 3. Perform semantic search
print("\nSemantic search for 'science fiction movie':")
print(kg.semantic_search("science fiction movie", top_k=2))

# 4. Find path between actors
print("\nPath between Leonardo DiCaprio and Christian Bale:")
print(kg.find_path(leo_id, bale_id))

# 5. Get entity details
print("\nDetails for Christopher Nolan:")
print(kg.get_entity_details(nolan_id))

# 6. Get nearby entities
print("\nEntities near Inception:")
print(kg.get_nearby_entities(inception_id))

# 7. Get graph statistics
print("\nKnowledge Graph Statistics:")
stats = kg.get_entity_statistics()
for key, value in stats.items():
    print(f"{key}: {value}")

# 8. Find central entities
print("\nMost central entities:")
central_entities = kg.get_central_entities(method='betweenness', top_k=3)
for entity_id, centrality in central_entities:
    print(f"Entity: {entity_id}, Centrality: {centrality:.3f}")

# 9. Save the knowledge graph
kg.save_to_file("movie_knowledge_graph.json")

# 10. Create visualizations
kg.visualize(output_file="movie_graph")  # Creates movie_graph.png
kg.visualize_interactive_plotly(save_html="movie_graph_interactive.html")