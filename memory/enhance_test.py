from enhanced_knowledge_graph import EnhancedGeneralizedKnowledgeGraph, Entity, EntityQuery


def main():
    # Create a new knowledge graph
    kg = EnhancedGeneralizedKnowledgeGraph()

    # Add entities
    print("Adding entities to the knowledge graph...")

    person1_id = kg.add_entity(Entity(entity_type="Person", attributes={
        "name": "John Doe",
        "age": 30,
        "occupation": "Software Engineer"
    }))

    person2_id = kg.add_entity(Entity(entity_type="Person", attributes={
        "name": "Jane Smith",
        "age": 28,
        "occupation": "Data Scientist"
    }))

    company1_id = kg.add_entity(Entity(entity_type="Company", attributes={
        "name": "Tech Innovations Inc.",
        "industry": "Technology",
        "founded": 2010
    }))

    project1_id = kg.add_entity(Entity(entity_type="Project", attributes={
        "name": "AI Assistant",
        "status": "In Progress",
        "start_date": "2023-01-15"
    }))

    # Add relationships
    print("\nAdding relationships between entities...")

    kg.add_relationship(person1_id, "WORKS_FOR", company1_id, {"start_date": "2020-05-01"})
    kg.add_relationship(person2_id, "WORKS_FOR", company1_id, {"start_date": "2021-03-15"})
    kg.add_relationship(person1_id, "WORKS_ON", project1_id, {"role": "Lead Developer"})
    kg.add_relationship(person2_id, "WORKS_ON", project1_id, {"role": "Data Analyst"})
    kg.add_relationship(company1_id, "OWNS", project1_id)

    # Query entities
    print("\nQuerying entities:")

    person_query = EntityQuery(entity_type="Person", attribute_filter={"occupation": "Software Engineer"})
    print(kg.query_entities(person_query))

    # Query relationships
    print("\nQuerying relationships for John Doe:")
    print(kg.query_relationships(person1_id))

    # Find path between entities
    print("\nFinding path between Jane Smith and the AI Assistant project:")
    print(kg.find_path(person2_id, project1_id))

    # Get entity details
    print("\nGetting details for Tech Innovations Inc.:")
    print(kg.get_entity_details(company1_id))

    # Get nearby entities
    print("\nGetting nearby entities for John Doe:")
    print(kg.get_nearby_entities(person1_id, max_distance=2))

    # Perform semantic search
    print("\nPerforming semantic search for 'tech company':")
    search_results = kg.semantic_search("tech company", top_k=2)
    for result in search_results:
        print(f"Entity ID: {result['entity_id']}")
        print(f"Similarity: {result['similarity']:.4f}")
        print(f"Type: {result['entity_type']}")
        print(f"Attributes: {result['attributes']}")
        print()

    # Update an entity
    print("\nUpdating John Doe's age:")
    print(kg.update_entity(person1_id, {"age": 31}))
    print(kg.get_entity_details(person1_id))

    # Delete an entity
    print("\nDeleting the AI Assistant project:")
    print(kg.delete_entity(project1_id))

    # Try to find a path to the deleted entity
    print("\nAttempting to find a path to the deleted project:")
    print(kg.find_path(person1_id, project1_id))

    # Save the knowledge graph to a file
    kg.save_to_file("example_knowledge_graph.json")
    print("\nKnowledge graph saved to 'example_knowledge_graph.json'")

    # Load the knowledge graph from the file
    loaded_kg = EnhancedGeneralizedKnowledgeGraph.load_from_file("example_knowledge_graph.json")
    print("\nKnowledge graph loaded from 'example_knowledge_graph.json'")

    # Verify the loaded graph by performing a query
    print("\nVerifying loaded graph - Querying persons:")
    person_query = EntityQuery(entity_type="Person")
    print(loaded_kg.query_entities(person_query))

    # Visualize the knowledge graph
    loaded_kg.visualize(output_file="example_knowledge_graph", format="png")
    print("\nKnowledge graph visualization saved as 'example_knowledge_graph.png'")


if __name__ == "__main__":
    main()

    # Create an instance of the enhanced knowledge graph
    kg = EnhancedGeneralizedKnowledgeGraph()

    # Add some entities
    kg.add_entity(Entity(entity_type="Person", attributes={"name": "John Doe", "age": 30}))
    kg.add_entity(Entity(entity_type="Person", attributes={"name": "Jane Smith", "age": 100}))
    kg.add_entity(Entity(entity_type="Company", attributes={"name": "Acme Corp", "industry": "Technology"}))

    # Perform a semantic search
    results = kg.semantic_search("Person, John Doe, 30", top_k=2)
    for result in results:
        print(f"Entity ID: {result['entity_id']}")
        print(f"Similarity: {result['similarity']}")
        print(f"Type: {result['entity_type']}")
        print(f"Attributes: {result['attributes']}")
        print()
