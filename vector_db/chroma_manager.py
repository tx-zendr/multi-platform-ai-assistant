import os
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()


class ChromaManager:

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="user_documents")
        self.gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def create_embedding(self, text: str):
        """Generates semantic vectors using the supported Developer API model."""
        try:
            response = self.gemini.models.embed_content(
                model="gemini-embedding-001",  # Fixed: Restored working Developer API model
                contents=text
            )
            # Extracted correctly out of the embeddings list payload array
            return response.embeddings[0].values
        except Exception as e:
            print(f"Embedding creation error: {e}")
            raise e

    def add_document(self, user_id: str, document_name: str, chunk_id: str, text: str):
        embedding = self.create_embedding(text)
        self.collection.add(
            ids=[str(chunk_id)],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"user_id": str(user_id), "document": document_name}]
        )

    def search(self, user_id: str, query: str, top_k: int = 3):
        query_embedding = self.create_embedding(query)
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"user_id": str(user_id)}
            )
            return results
        except Exception as e:
            print(f"Vector search execution error: {e}")
            return {"documents": [[]], "metadatas": [[]]}