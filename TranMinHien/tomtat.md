# Tóm tắt công việc cá nhân — Phase 1, Lab 7

## 1. Mục tiêu của bài

Phase 1 yêu cầu xây dựng một pipeline RAG nhỏ bằng Python:

```text
tài liệu → chia chunk → tạo embedding → lưu vector → tìm kiếm → tạo prompt → agent trả lời
```

Mục tiêu là hiểu cách văn bản được chuẩn bị, lưu trữ dưới dạng vector và được truy xuất để làm context cho một agent hỏi đáp.

## 2. Những phần đã hoàn thiện

### Chunking — `src/chunking.py`

- `SentenceChunker`: tách văn bản theo dấu `.`, `!`, `?`, sau đó gom một số câu cố định vào mỗi chunk. Cách này giúp hạn chế cắt giữa câu và giữ ý nghĩa dễ đọc hơn.
- `RecursiveChunker`: thử tách theo cấu trúc lớn trước như đoạn văn và xuống dòng, sau đó mới xuống câu, khoảng trắng và cuối cùng là cắt ký tự. Cách này linh hoạt khi tài liệu có độ dài và cấu trúc khác nhau.
- `compute_similarity`: tính cosine similarity bằng công thức dot product chia cho tích độ dài hai vector. Vector 0 được xử lý riêng để tránh chia cho 0.
- `ChunkingStrategyComparator`: chạy ba chiến lược built-in và trả về số lượng chunk, độ dài trung bình và nội dung chunk để so sánh.

### Vector store — `src/store.py`

- Mỗi `Document` được chuyển thành record gồm `id`, `content`, `metadata` và `embedding`.
- `add_documents` embedding từng tài liệu rồi lưu vào store.
- `search` embedding câu hỏi, tính dot product với các record và trả về kết quả có điểm cao nhất.
- `search_with_filter` lọc metadata trước khi tìm kiếm. Ví dụ có thể chỉ tìm tài liệu dành cho `customer_role=seller`.
- `get_collection_size` đếm số chunk đang lưu.
- `delete_document` xóa tài liệu hoặc toàn bộ chunk cùng `doc_id`.
- Có khởi tạo ChromaDB khi thư viện khả dụng, nhưng bộ nhớ trong vẫn là nguồn dữ liệu chính để hành vi test và metadata nhất quán trong mọi môi trường.

### RAG agent — `src/agent.py`

`KnowledgeBaseAgent.answer` thực hiện ba bước:

1. Tìm top-k chunk liên quan từ `EmbeddingStore`.
2. Ghép các chunk vào phần `CONTEXT` của prompt.
3. Gọi `llm_fn` để sinh câu trả lời.

Prompt cũng yêu cầu agent chỉ sử dụng context và nói rõ khi context không đủ, giúp giảm nguy cơ bịa thông tin.

## 3. Kết quả kiểm tra

Đã cài `pytest==9.1.1` trong virtual environment tạm và chạy đúng lệnh kiểm thử:

```text
/private/tmp/lab07-pytest-venv/bin/pytest tests/ -v
============================== 42 passed in 0.03s ==============================
```

Kết quả: **42/42 test pass**.

Ngoài ra, pipeline ingest cũng chạy thành công:

```text
ingest self-check OK: parse được 4 khóa metadata, tạo 18 chunk
```

Demo `main.py` nạp được 3 chunk từ dữ liệu K4 mẫu và thực hiện được search + agent answer.

## 4. Kiến thức rút ra

- Cosine similarity đo độ giống nhau về hướng của hai vector; với text embedding, hướng thường quan trọng hơn độ lớn.
- Overlap giúp giữ context ở ranh giới giữa hai chunk nhưng làm tăng số chunk và chi phí xử lý.
- Chunk quá nhỏ có thể làm mất ngữ cảnh; chunk quá lớn có thể chứa nhiều thông tin nhiễu. Chunk theo câu hoặc theo cấu trúc tài liệu thường dễ đọc hơn.
- Metadata không thay thế semantic search nhưng giúp giới hạn phạm vi tìm kiếm theo vai trò, danh mục hoặc nguồn.
- RAG không tự tạo kiến thức mới: chất lượng câu trả lời phụ thuộc vào chunk được truy xuất và prompt gửi cho LLM.
- Mock embedding của lab được tạo từ hash chuỗi nên có tính xác định, nhưng không hiểu nghĩa. Vì vậy mock phù hợp cho unit test, không phù hợp để kết luận câu nào gần nghĩa hơn trong tiếng Việt.

## 5. Giới hạn của kết quả benchmark

Báo cáo cá nhân dùng tạm hai tài liệu khởi động trong `data/k4_ecommerce/` vì báo cáo nhóm chưa có bộ 5 câu hỏi chính thức. Kết quả tạm cho thấy 4/5 câu có chunk liên quan trong top-3 khi dùng mock embedding. Các URL trong dữ liệu là URL mẫu; khi làm benchmark chính thức cần thay bằng nguồn công khai thật, bổ sung đủ 5–10 tài liệu và chạy lại với local multilingual embedder.

## 6. Cách chạy lại

```bash
/private/tmp/lab07-pytest-venv/bin/pytest tests/ -v
python3 ingest.py
python3 main.py "Người mua cần gì khi gửi yêu cầu đổi trả?"
```
