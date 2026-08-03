from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3, metadata_filter: dict | None = None) -> str:
        records = self.store.search_with_filter(
            question,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )
        records_text = ""
        for i, record in enumerate(records):
            records_text += f"[{i}] doc_id: {record["id"]} " 
            context = record["metadata"].get("parent_context", record["content"])
            records_text += f"{context} "
        prompt = f"""
        Instruction: chỉ dùng context; nói rõ khi context không đủ.\n
        Context: {records_text}\n
        Question: {question}\n
        Answer:
        """
        ans = self.llm_fn(prompt)
        return prompt + ans
