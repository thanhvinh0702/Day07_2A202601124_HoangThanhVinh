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


class DocumentStructuredChunker:
    """Split Markdown-like documents by headings while preserving section context.

    Each heading starts a semantic section. Sections longer than ``chunk_size``
    are packed by paragraph (then by words), and the heading is prefixed to
    every child chunk so later chunks do not lose their document context.
    """

    HEADING_RE = re.compile(r"(?m)^#{1,6}\s+.+$" )

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
