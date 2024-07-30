import json
import uuid

import re
from typing import List, Dict

import chromadb
from chromadb.utils import embedding_functions
from ragatouille import RAGPretrainedModel

from chat_history import ChatFormatter, ChatHistory
from chat_api import ChatAPI, LlamaAgentProvider


class RAGColbertReranker:
    """
    Represents a chromadb vector database with a Colbert reranker.
    """

    def __init__(
            self,
            persistent_db_path="./retrieval_memory",
            embedding_model_name="BAAI/bge-small-en-v1.5",
            collection_name="retrieval_memory_collection",
            persistent: bool = True,
    ):
        self.RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
        if persistent:
            self.client = chromadb.PersistentClient(path=persistent_db_path)
        else:
            self.client = chromadb.EphemeralClient()
        self.sentence_transformer_ef = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model_name
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.sentence_transformer_ef
        )

    def add_document(self, document: str, metadata: dict = None):
        """Add a memory with a given description and importance to the memory stream."""
        mem = [document]
        ids = [str(self.generate_unique_id())]
        self.collection.add(documents=mem, metadatas=metadata, ids=ids)

    def retrieve_documents(self, query: str, k, metadata_filter: dict = None):
        query_embedding = self.sentence_transformer_ef([query])
        query_result = self.collection.query(
            query_embedding,
            n_results=k,
            include=["metadatas", "embeddings", "documents", "distances"],
        )
        documents = []
        for doc, metadata in zip(query_result["documents"][0], query_result["metadatas"][0]):
            # implement filtering
            documents.append(doc)
        results = self.RAG.rerank(query=query, documents=documents, k=k)
        return results

    @staticmethod
    def generate_unique_id():
        unique_id = str(uuid.uuid4())
        return unique_id


class GameInformationMetadata:
    def __init__(self):
        self.involved_persons = []
        self.topics = []
        self.important_items = []
        self.locations = []

    def to_dict(self):
        return {
            "involved_persons": '\n'.join(self.involved_persons),
            "topics": '\n'.join(self.topics),
            "important_items": '\n'.join(self.important_items),
            "locations": '\n'.join(self.locations)
        }


class GameInformation:
    def __init__(self, messages: List[Dict], chat_api: ChatAPI):
        self.messages = messages
        self.api = chat_api
        self.metadata = GameInformationMetadata()
        template = "{role}: {content}\n\n"
        role_names = {
            "assistant": "Game Master",
            "user": "Player"
        }
        formatter = ChatFormatter(template, role_names)
        self.formatted_chat = formatter.format_messages(self.messages)

    def get_metadata_as_dict(self):
        return self.metadata.to_dict()

    def get_formatted_chat(self):
        return self.formatted_chat

    def generate_metadata(self):
        prompt = """Analyze the following game messages and extract key information: main characters involved, topics discussed, locations mentioned, and important items. Format your response in XML-tags, like in the following examples:

<involved_persons>
Jack Applebaum, Theo Long, Marie Meyer
</involved_persons>

<topics>
treasure hunt, magical artifacts, ancient prophecy
</topics>

<important_items>
enchanted compass, dragon scale, mystic map
</important_items>

<locations>
Whispering Woods, Crystal Cavern, Sunken City
</locations>

Ensure each category is on a single line, with multiple entries separated by commas. If a category has no relevant information, leave it empty but include the tags. Here's the game conversation to analyze:

""" + self.formatted_chat

        response = self.api.get_response([{"role": "user", "content": prompt}])
        self.parse_metadata(response)

    def parse_metadata(self, response):
        def extract_content(tag):
            pattern = f"<{tag}>(.*?)</{tag}>"
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return [item.strip() for item in match.group(1).split(',') if item.strip()]
            return []

        self.metadata.involved_persons = extract_content("involved_persons")
        self.metadata.topics = extract_content("topics")
        self.metadata.important_items = extract_content("important_items")
        self.metadata.locations = extract_content("locations")


def split_into_packages(elements, max_size=2):
    return [elements[i:i + max_size] for i in range(0, len(elements), max_size)]


def init_test(database, chat, chat_api):
    packages = split_into_packages(chat)

    game_information_list = []
    for package in range(0, len(packages) - 10):
        game_information_list.append(GameInformation(packages[package], chat_api))

    for game_information in game_information_list:
        game_information.generate_metadata()
        database.add_document(game_information.get_formatted_chat(), game_information.get_metadata_as_dict())


template = "{role}: {content}\n\n"
role_names = {
    "assistant": "Game Master",
    "user": "Player"
}
formatter = ChatFormatter(template, role_names)

vector_database = RAGColbertReranker()
api = LlamaAgentProvider("http://127.0.0.1:8080", "")
history = ChatHistory("chat_history/new_gameClaude")

history.load_history()
chat_list = history.to_list()

init_test(vector_database, chat_list, api)

last_3_messages = chat_list[-4:]

results = vector_database.retrieve_documents("What information is most relevant to the following context?\n\nContext:\n" + formatter.format_messages(last_3_messages), k=10)

for result in results:
    print(result["score"])
    print(result["content"])
    print("\n\n\n---------------")
