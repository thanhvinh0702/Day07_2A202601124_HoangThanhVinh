from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # TODO: split into sentences, group into chunks
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
        return [" ".join(sentences[index : index + self.max_sentences_per_chunk]) for index in range(0, len(sentences), self.max_sentences_per_chunk)]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # TODO: implement recursive splitting strategy
        if len(text) == 0:
            return text
        return self._split(text, self.DEFAULT_SEPARATORS)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [current_text]

        separator = remaining_separators[0]
        if separator == "":
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        parts = current_text.split(separator)
        if len(parts) == 1:
            return self._split(current_text, remaining_separators[1:])

        chunks: list[str] = []
        next_separators = remaining_separators[1:]
        for part in parts:
            if not part:
                continue
            if len(part) <= self.chunk_size:
                chunks.append(part)
            else:
                chunks.extend(self._split(part, next_separators))
        return chunks


class ParentChildChunker:
    """
    Split text into large parent chunks, then split each parent into smaller child chunks.

    Rules:
        - Text is first split into parent chunks via RecursiveChunker(chunk_size=parent_chunk_size).
        - Each parent is then split into child chunks via FixedSizeChunker(chunk_size=child_chunk_size, overlap=child_overlap).
        - Each child keeps a reference to its parent (parent_id, parent_text) so retrieval can
          search over the smaller, more precise children while returning the fuller parent
          context for generation.
        - Returns [] for empty text.
    """

    def __init__(
        self,
        parent_chunk_size: int = 2000,
        child_chunk_size: int = 400,
        child_overlap: int = 50,
    ) -> None:
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap
        self._parent_splitter = RecursiveChunker(chunk_size=parent_chunk_size)
        self._child_splitter = FixedSizeChunker(chunk_size=child_chunk_size, overlap=child_overlap)

    def chunk(self, text: str) -> list[dict]:
        if not text:
            return []

        results: list[dict] = []
        parents = self._parent_splitter.chunk(text)
        for parent_id, parent_text in enumerate(parents):
            children = self._child_splitter.chunk(parent_text)
            for child_id, child_text in enumerate(children):
                results.append(
                    {
                        "parent_id": parent_id,
                        "parent_text": parent_text,
                        "child_id": child_id,
                        "child_text": child_text,
                    }
                )
        return results


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot = _dot(vec_a, vec_b)
    norm_a_sq = math.sqrt(_dot(vec_a, vec_a))
    norm_b_sq = math.sqrt(_dot(vec_b, vec_b))
    return dot / (norm_a_sq * norm_b_sq) if (norm_a_sq * norm_b_sq) else 0.0


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size),
            "by_sentences": SentenceChunker(),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }
        comparison = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            comparison[name] = {
                "count": count,
                "avg_length": sum(map(len, chunks)) / count if count else 0.0,
                "chunks": chunks,
            }
        return comparison
