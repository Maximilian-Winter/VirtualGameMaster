import json
import uuid

from typing import List, Dict, Optional

import chromadb
from chromadb.utils import embedding_functions
from ragatouille import RAGPretrainedModel

from VirtualGameMaster.chat_history import ChatFormatter, ChatHistory


class ChatTurnRAG:
    def __init__(
            self,
            persistent_db_path: str = "./retrieval_memory",
            embedding_model_name: str = "BAAI/bge-small-en-v1.5",
            collection_name: str = "retrieval_memory_collection",
            persistent: bool = True,
            reranker_model_name: str = "colbert-ir/colbertv2.0",
    ):
        self.RAG = RAGPretrainedModel.from_pretrained(reranker_model_name)
        self.client = (
            chromadb.PersistentClient(path=persistent_db_path)
            if persistent
            else chromadb.EphemeralClient()
        )
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model_name
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.sentence_transformer_ef
        )

    def add_formatted_chat_turn(self, chat_turn: str, metadata: Optional[Dict] = None) -> str:
        id = str(uuid.uuid4())
        try:
            self.collection.add(documents=[chat_turn], ids=[id], metadatas=[metadata] if metadata else None)
            return id
        except Exception as e:
            print(f"Error adding chat turn: {e}")
            return ""

    def add_multiple_chat_turns(self, chat_turns: List[str], metadatas: Optional[List[Dict]] = None) -> List[str]:
        ids = [str(uuid.uuid4()) for _ in chat_turns]
        try:
            self.collection.add(
                documents=chat_turns,
                ids=ids,
                metadatas=metadatas if metadatas else None
            )
            return ids
        except Exception as e:
            print(f"Error adding multiple chat turns: {e}")
            return []

    def retrieve_chat_turns(self, query: str, k: int, initial_multiplier: int = 4) -> List[Dict]:
        if self.collection.count() == 0:
            return []
        try:
            query_embedding = self.sentence_transformer_ef([query])
            query_result = self.collection.query(
                query_embedding,
                n_results=min(k * initial_multiplier, self.collection.count()),
                include=["documents", "metadatas"],
            )
            documents = query_result["documents"][0]
            results = self.RAG.rerank(query=query, documents=documents, k=min(k, len(documents)))
            for i, result in enumerate(results):
                result["metadata"] = query_result["metadatas"][0][i] if query_result["metadatas"] else None
            return results
        except Exception as e:
            print(f"Error retrieving chat turns: {e}")
            return []

    def get_chat_turn_count(self) -> int:
        return self.collection.count()

    def delete_chat_turn(self, id: str) -> bool:
        try:
            self.collection.delete(ids=[id])
            return True
        except Exception as e:
            print(f"Error deleting chat turn: {e}")
            return False

    def update_chat_turn(self, id: str, new_content: str, new_metadata: Optional[Dict] = None) -> bool:
        try:
            self.collection.update(
                ids=[id],
                documents=[new_content],
                metadatas=[new_metadata] if new_metadata else None
            )
            return True
        except Exception as e:
            print(f"Error updating chat turn: {e}")
            return False


class ChatTurnFormatter:
    def __init__(self, messages: List[Dict], role_names=None):
        if role_names is None:
            role_names = {
                "assistant": "Assistant",
                "user": "User"
            }
        self.messages = messages
        template = "{role}: {content}\n\n"

        formatter = ChatFormatter(template, role_names)
        self.formatted_chat = formatter.format_messages(self.messages)

    def get_formatted_chat(self):
        return self.formatted_chat

    @staticmethod
    def get_chat_turn_list(messages: List[Dict], role_names=None) -> List[Dict]:
        return [ChatTurnFormatter(messages[i:i + 2], role_names=role_names) for i in range(0, len(messages), 2)]

