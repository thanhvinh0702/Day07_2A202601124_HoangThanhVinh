from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": dict(doc.metadata or {}),
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0:
            return []

        query_embedding = self._embedding_fn(query)
        scored: list[dict[str, Any]] = []
        for record in records:
            result = dict(record)
            result["metadata"] = dict(record.get("metadata") or {})
            result["score"] = _dot(query_embedding, record["embedding"])
            scored.append(result)
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        for doc in docs:
            record = self._make_record(doc)
            record["_store_id"] = f"{self._collection_name}::{self._next_index}"
            self._next_index += 1
            self._store.append(record)

            # Chroma is kept as an optional mirror.  The in-memory records stay
            # canonical so duplicate document IDs and metadata filtering behave
            # identically in every environment.
            if self._use_chroma and self._collection is not None:
                chroma_metadata: dict[str, Any] = {}
                for key, value in record["metadata"].items():
                    if isinstance(value, (str, int, float, bool)):
                        chroma_metadata[str(key)] = value
                    elif value is not None:
                        chroma_metadata[str(key)] = str(value)
                chroma_metadata.setdefault("__document_id", doc.id)
                try:
                    self._collection.add(
                        ids=[record["_store_id"]],
                        documents=[record["content"]],
                        embeddings=[record["embedding"]],
                        metadatas=[chroma_metadata],
                    )
                except Exception:
                    # Retrieval remains available through the canonical memory
                    # store if an optional Chroma installation rejects metadata.
                    self._use_chroma = False

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        filtered = [
            record
            for record in self._store
            if all(record.get("metadata", {}).get(key) == value
                   for key, value in metadata_filter.items())
        ]
        return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        removed = [
            record
            for record in self._store
            if record.get("id") == doc_id
            or record.get("metadata", {}).get("doc_id") == doc_id
        ]
        if not removed:
            return False

        removed_ids = {record.get("_store_id") for record in removed}
        self._store = [
            record for record in self._store
            if record.get("_store_id") not in removed_ids
        ]
        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(ids=[rid for rid in removed_ids if rid])
            except Exception:
                self._use_chroma = False
        return True
