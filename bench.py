"""Run the fixed five-query retrieval benchmark for one chunking strategy."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import DocumentStructuredChunker, FixedSizeChunker, RecursiveChunker
from src.embeddings import OPENAI_EMBEDDING_MODEL, OpenAIEmbedder


QUERIES = [
    ("Số liệu", "Khách hàng có bao nhiêu ngày để gửi yêu cầu trả hàng/hoàn tiền sau khi đơn được cập nhật là ‘Đã giao hàng’?", None),
    ("Điều kiện", "Nhà bán hàng có thể hủy đơn hàng TikTok Shop đến thời điểm nào?", None),
    ("Quy trình", "Nếu nhà bán hàng từ chối yêu cầu trả hàng/hoàn tiền, khách hàng cần làm gì và trong bao lâu?", None),
    ("Liệt kê", "Khi vi phạm chính sách, nền tảng có thể áp dụng những biện pháp nào đối với nhà sáng tạo?", {"customer_role": "creator"}),
    ("Ngoại lệ", "Đơn có nhiều sản phẩm và dùng voucher miễn phí vận chuyển có được hủy một phần không?", None),
]


def make_openai_llm(model: str, max_tokens: int):
    from openai import OpenAI

    options = {}
    if os.getenv("OPENAI_BASE_URL"):
        options["base_url"] = os.environ["OPENAI_BASE_URL"]
    client = OpenAI(**options)

    def generate(prompt: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    return generate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/k4_ecommerce_crawled")
    parser.add_argument("--strategy", choices=("document_structured", "recursive", "fixed"), default="document_structured")
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--output", type=Path, default=Path("bench_results.txt"))
    parser.add_argument("--embedding-model", default=None)
    parser.add_argument("--llm-model", default=None)
    args = parser.parse_args()

    load_dotenv(dotenv_path=Path(".env"), override=False)
    embedding_model = args.embedding_model or os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL)
    llm_model = args.llm_model or os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "512"))
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY chưa được cấu hình")

    if args.strategy == "document_structured":
        chunker = DocumentStructuredChunker(chunk_size=args.chunk_size)
    elif args.strategy == "fixed":
        chunker = FixedSizeChunker(chunk_size=args.chunk_size, overlap=min(50, args.chunk_size // 4))
    else:
        chunker = RecursiveChunker(chunk_size=args.chunk_size)
    embedding_fn = OpenAIEmbedder(model_name=embedding_model)
    batch_size = 200
    embedding_calls = 0

    def embedding_batch_with_progress(texts: list[str]) -> list[list[float]]:
        nonlocal embedding_calls
        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            vectors.extend(embedding_fn.embed_batch(batch))
            embedding_calls += len(batch)
            print(f"Embedding progress: {embedding_calls}/{len(texts)} chunks", flush=True)
        return vectors

    print(f"Loading corpus: {args.data_dir}", flush=True)
    store = build_knowledge_base(
        args.data_dir,
        embedding_fn,
        chunker=chunker,
        embedding_batch_fn=embedding_batch_with_progress,
    )
    print(f"Embedding complete: {embedding_calls} chunks", flush=True)
    agent = KnowledgeBaseAgent(store=store, llm_fn=make_openai_llm(llm_model, max_tokens))

    output: list[str] = []

    def emit(line: str = "") -> None:
        print(line)
        output.append(line)

    emit(f"strategy={args.strategy} chunk_size={args.chunk_size}")
    emit(f"embedding_model={embedding_model} llm_model={llm_model} max_tokens={max_tokens}")
    emit(f"chunks_loaded={store.get_collection_size()}")
    for index, (kind, question, metadata_filter) in enumerate(QUERIES, start=1):
        print(f"Query progress: {index}/{len(QUERIES)}", flush=True)
        results = store.search_with_filter(question, top_k=3, metadata_filter=metadata_filter)
        emit(f"\nQ{index} [{kind}] filter={metadata_filter or {}}: {question}")
        for rank, result in enumerate(results, start=1):
            preview = " ".join(result["content"].split())[:180]
            emit(f"  top-{rank} score={result['score']:.4f} doc_id={result['metadata'].get('doc_id')} preview={preview}")
        emit("  agent: " + agent.answer(question, top_k=3, metadata_filter=metadata_filter))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"\nSaved benchmark output to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
