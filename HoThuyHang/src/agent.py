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

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)

        context_lines = []
        for i, result in enumerate(results, start=1):
            source = result.get("metadata", {}).get("doc_id", "unknown")
            context_lines.append(f"[{i}] (source: {source}) {result['content']}")
        context = "\n".join(context_lines)

        prompt = (
            "Answer the question using only the context below. "
            "If the context does not contain the answer, say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

        return self.llm_fn(prompt)
