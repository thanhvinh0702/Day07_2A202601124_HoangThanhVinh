"""
bench.py — Script chạy Benchmark truy xuất cho Lab 7 (Checkpoint 5).

Nhiệm vụ:
    1. Khởi tạo RecursiveChunker (Chiến lược cá nhân của Trần Minh Hiển).
    2. Nạp toàn bộ bộ dữ liệu tại data/k4_ecommerce qua ingest.build_knowledge_base().
    3. Chạy bộ 5 Benchmark Queries (gồm cả tìm kiếm thường và search_with_filter).
    4. In ra tổng số chunk, thông số strategy, top-3 kết quả truy xuất và câu trả lời của agent.
"""
from __future__ import annotations

import hashlib
from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker


def _mock_embed(text: str) -> list[float]:
    """Tạo vector giả lập 8 chiều ổn định dựa trên MD5 hash của text."""
    digest = hashlib.md5(text.encode("utf-8")).digest()
    return [float(b) / 255.0 for b in digest[:8]]


def _demo_llm(prompt: str) -> str:
    """LLM giả lập để in ra preview của prompt mà không cần API key."""
    return f"[DEMO LLM RESPONSE BASED ON RETRIEVED CONTEXT]\n{prompt[:300]}..."


def run_benchmark():
    # 1. Chọn chiến lược chunker của cá nhân
    chunker_strategy = RecursiveChunker(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=500
    )
    print("=" * 70)
    print("🚀 CHẠY BENCHMARK TRUY XUẤT (CHECKPOINT 5)")
    print("=" * 70)
    print(f"📌 Chiến lược Chunker: RecursiveChunker (chunk_size=500, separators=['\\n\\n', '\\n', '. ', ' '])")
    print(f"📁 Thư mục dữ liệu: data/k4_ecommerce")

    # 2. Nạp dữ liệu qua ingest.py
    store = build_knowledge_base(
        data_dir="data/k4_ecommerce",
        embedding_fn=_mock_embed,
        chunker=chunker_strategy,
        collection_name="bench_ecommerce"
    )
    agent = KnowledgeBaseAgent(store=store, llm_fn=_demo_llm)
    total_chunks = store.get_collection_size()
    print(f"✅ Đã nạp thành công: {total_chunks} chunks vào Vector Store\n")

    # 3. Danh sách 5 Benchmark Queries
    benchmark_queries = [
        {
            "id": 1,
            "type": "Số liệu (Numbers)",
            "query": "Mã OTP đăng nhập Shopee có hiệu lực trong bao lâu?",
            "gold_answer": "Mã OTP đăng nhập Shopee có hiệu lực trong vòng 60 giây kể từ khi nhận được.",
            "filter": None
        },
        {
            "id": 2,
            "type": "Điều kiện (Conditions)",
            "query": "Đơn hàng Shopee bị chậm cập nhật trạng thái do những nguyên nhân nào?",
            "gold_answer": "Do đơn vị vận chuyển chưa cập nhật hệ thống hoặc trong dịp lễ/cuối tuần.",
            "filter": None
        },
        {
            "id": 3,
            "type": "Quy trình (Processes)",
            "query": "Người mua cần làm gì khi quá hạn thanh toán hóa đơn SPayLater?",
            "gold_answer": "Người mua cần thanh toán ngay qua ví ShopeePay hoặc tài khoản ngân hàng để tránh phí quá hạn.",
            "filter": None
        },
        {
            "id": 4,
            "type": "Liệt kê (Lists)",
            "query": "Những nhóm sản phẩm nào bị cấm đăng bán trên TikTok Shop?",
            "gold_answer": "Vũ khí, chất cháy nổ, ma túy, tài sản trộm cắp, động vật hoang dã, hàng giả hàng nhái.",
            "filter": None
        },
        {
            "id": 5,
            "type": "Cần Filter Metadata (Role Filter)",
            "query": "Quy định hủy đơn hàng và trả hàng hoàn tiền áp dụng cho đối tượng nào?",
            "gold_answer": "Áp dụng cho Nhà bán hàng (Seller) trên TikTok Shop khi xử lý yêu cầu hủy đơn.",
            "filter": {"customer_role": "seller"}
        }
    ]

    # 4. Chạy từng query và in kết quả
    for bq in benchmark_queries:
        print("-" * 70)
        print(f"❓ Query #{bq['id']} [{bq['type']}]: {bq['query']}")
        print(f"🎯 Gold Answer: {bq['gold_answer']}")
        if bq['filter']:
            print(f"🔒 Metadata Filter áp dụng: {bq['filter']}")
            results = store.search_with_filter(bq['query'], top_k=3, metadata_filter=bq['filter'])
        else:
            print("🔍 Loạt tìm kiếm: Không filter")
            results = store.search(bq['query'], top_k=3)

        print("\n--- TOP-3 RETRIEVAL RESULTS ---")
        for i, res in enumerate(results, 1):
            doc_id = res['metadata'].get('doc_id', 'N/A')
            chunk_idx = res['metadata'].get('chunk_index', 'N/A')
            score = res.get('score', 0.0)
            preview = res['content'].replace('\n', ' ')[:100]
            print(f"  [{i}] Score: {score:.4f} | doc_id: {doc_id} (chunk {chunk_idx})")
            print(f"      Snippet: \"{preview}...\"")

        print("\n🤖 AGENT ANSWER:")
        agent_resp = agent.answer(bq['query'], top_k=3)
        print(f"   {agent_resp.strip()}")
        print("-" * 70 + "\n")


if __name__ == "__main__":
    run_benchmark()
