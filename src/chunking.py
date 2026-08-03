from __future__ import annotations

import math
import re
from collections.abc import Callable, Sequence


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


class SemanticChunker:
    """Group neighbouring sentences while they remain semantically similar.

    ``embedding_function`` may be supplied as ``Callable[[str], Sequence[float]]``
    (for example, a sentence-transformer wrapper).  Without one, a small
    bag-of-words embedding is used so the class remains dependency-free.
    A new chunk is started when similarity with the current chunk falls below
    ``similarity_threshold`` or ``max_chunk_size`` would be exceeded.
    """

    def __init__(
        self,
        embedding_function: Callable[[str], Sequence[float]] | None = None,
        similarity_threshold: float = 0.55,
        max_chunk_size: int = 500,
    ) -> None:
        if max_chunk_size < 1:
            raise ValueError("max_chunk_size must be positive")
        self.embedding_function = embedding_function
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size

    @staticmethod
    def _fallback_embedding(text: str) -> list[float]:
        tokens = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
        counts: dict[str, float] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0.0) + 1.0
        # Stable dimensions are sufficient for comparing two texts locally.
        return [counts[key] for key in sorted(counts)]

    def _embed(self, text: str) -> Sequence[float]:
        return self.embedding_function(text) if self.embedding_function else self._fallback_embedding(text)

    def _similarity(self, left: str, right: str) -> float:
        if self.embedding_function is not None:
            return compute_similarity(list(self._embed(left)), list(self._embed(right)))
        left_tokens = set(re.findall(r"\w+", left.lower(), flags=re.UNICODE))
        right_tokens = set(re.findall(r"\w+", right.lower(), flags=re.UNICODE))
        if not left_tokens or not right_tokens:
            return 0.0
        return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
        chunks: list[str] = []
        current = sentences[0]
        for sentence in sentences[1:]:
            candidate = f"{current} {sentence}"
            similarity = self._similarity(current, sentence)
            if len(candidate) <= self.max_chunk_size and similarity >= self.similarity_threshold:
                current = candidate
                current_embedding = self._embed(current)
            else:
                chunks.append(current)
                current = sentence
        chunks.append(current)
        return chunks


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
            "semantic": SemanticChunker(max_chunk_size=chunk_size),
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
