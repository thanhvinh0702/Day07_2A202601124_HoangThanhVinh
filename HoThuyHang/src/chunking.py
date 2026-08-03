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
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
        return [
            " ".join(sentences[index : index + self.max_sentences_per_chunk])
            for index in range(0, len(sentences), self.max_sentences_per_chunk)
        ]


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
        if not text:
            return []
        return self._split(text, self.separators)

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


class DocumentStructuredChunker:
    """Split Markdown-like documents by headings while preserving section context."""

    HEADING_RE = re.compile(r"(?m)^(?:#{1,6}\s+.+|\d+(?:\.\d+){0,5}\s+[^\n]+)$")

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = max(1, chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        matches = list(self.HEADING_RE.finditer(text))
        if not matches:
            return self._split_body(text.strip(), "")

        sections: list[tuple[str, str]] = []
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                sections.append(("", preamble))

        for index, match in enumerate(matches):
            heading = match.group(0).strip()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[match.end() : end].strip()
            sections.append((heading, body))

        chunks: list[str] = []
        for heading, body in sections:
            chunks.extend(self._split_body(body, heading))
        return chunks

    def _split_body(self, body: str, heading: str) -> list[str]:
        prefix = f"{heading}\n\n" if heading else ""
        available = self.chunk_size - len(prefix)
        if available <= 0:
            return [prefix[: self.chunk_size]]
        if len(body) <= available:
            return [prefix + body] if body else ([heading] if heading else [])

        units = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
        if not units:
            units = [body]

        chunks: list[str] = []
        current = ""
        for unit in units:
            if len(unit) > available:
                if current:
                    chunks.append(prefix + current)
                    current = ""
                chunks.extend(self._hard_split(unit, prefix, available))
                continue

            candidate = f"{current}\n\n{unit}" if current else unit
            if len(candidate) > available:
                if current:
                    chunks.append(prefix + current)
                current = unit
            else:
                current = candidate

        if current:
            chunks.append(prefix + current)
        return chunks

    @staticmethod
    def _hard_split(text: str, prefix: str, available: int) -> list[str]:
        return [prefix + text[start : start + available] for start in range(0, len(text), available)]


class SemanticChunker:
    """Group neighbouring sentences while they remain semantically similar."""

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
        if not sentences:
            return []

        chunks: list[str] = []
        current = sentences[0]
        for sentence in sentences[1:]:
            candidate = f"{current} {sentence}"
            similarity = self._similarity(current, sentence)
            if len(candidate) <= self.max_chunk_size and similarity >= self.similarity_threshold:
                current = candidate
            else:
                chunks.append(current)
                current = sentence
        chunks.append(current)
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
            "document_structured": DocumentStructuredChunker(chunk_size=chunk_size),
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
