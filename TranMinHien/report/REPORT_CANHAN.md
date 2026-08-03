# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Minh Hiền
**Nhóm:** [Tên nhóm]
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có cùng hướng hoặc gần cùng hướng, nghĩa là hai văn bản có biểu diễn ngữ nghĩa tương đối giống nhau. Giá trị càng gần 1 thì mức tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Mèo đang ngồi trên thảm.
- Câu B: Một con mèo ngồi trên tấm thảm.
- Tại sao tương đồng: Hai câu mô tả gần như cùng một sự việc, dù cách dùng từ hơi khác.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Người mua gửi yêu cầu đổi trả hàng.
- Câu B: Rừng cây nằm ở phía bắc.
- Tại sao khác: Hai câu nói về hai chủ đề không liên quan: chính sách mua hàng và địa lý tự nhiên.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, nên ít bị ảnh hưởng bởi độ lớn tuyệt đối của embedding. Điều này phù hợp với text embedding vì hướng thường biểu diễn ý nghĩa tốt hơn độ dài vector.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.11) = 23`.
>
> **Đáp án: 23 chunks.**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap bằng 100, số chunk là `ceil((10,000 - 100) / (500 - 100)) = ceil(24.75) = 25 chunks`. Overlap lớn hơn giúp giữ lại ngữ cảnh ở ranh giới giữa hai chunk, nhưng làm tăng số chunk, chi phí embedding và khả năng trùng lặp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Hàm dùng regex `(?<=[.!?])\s+` để tách sau dấu kết thúc câu, đồng thời giữ lại dấu câu trong câu. Văn bản rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng; các câu được làm sạch khoảng trắng rồi gom thành nhóm tối đa `max_sentences_per_chunk` câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử các separator theo thứ tự ưu tiên: đoạn văn, xuống dòng, kết thúc câu, khoảng trắng và cuối cùng là tách ký tự. Base case là văn bản đã ngắn hơn hoặc bằng `chunk_size`; nếu không còn separator thì dùng hard split để luôn bảo đảm tiến triển và không bị đệ quy vô hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuyển thành record gồm ID, nội dung, metadata và embedding; record được lưu trong bộ nhớ và có thể đồng bộ sang ChromaDB nếu thư viện khả dụng. Khi tìm kiếm, query cũng được embedding rồi tính dot product với từng embedding đã lưu, sắp xếp điểm giảm dần và lấy `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc trước theo điều kiện metadata, sau đó mới tính điểm trên tập ứng viên nhỏ hơn. `delete_document` xóa các record có ID trùng hoặc có `metadata['doc_id']` trùng, nên có thể xóa toàn bộ các chunk thuộc cùng một tài liệu.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` truy xuất top-k chunk, đánh số và ghép nội dung vào phần `CONTEXT` của prompt. Prompt yêu cầu mô hình chỉ dùng context và báo rõ khi thiếu thông tin, sau đó truyền prompt cho `llm_fn` để tạo câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
/private/tmp/lab07-pytest-venv/bin/pytest tests/ -v
============================== 42 passed in 0.03s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Các điểm dưới đây được tính bằng `_mock_embed`. Mock embedder tạo vector từ hash toàn bộ chuỗi nên không phản ánh đúng ngữ nghĩa.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Mèo đang ngồi trên thảm. | Một con mèo ngồi trên tấm thảm. | cao | -0.1331 | Không |
| 2 | Người mua gửi yêu cầu đổi trả. | Người bán đăng sản phẩm chính xác. | thấp | 0.0077 | Có |
| 3 | Python dùng cho phân tích dữ liệu. | Python supports data analysis. | cao | -0.0630 | Không |
| 4 | Lỗi thanh toán cần kiểm tra. | Rừng cây nằm ở phía bắc. | thấp | -0.0286 | Có |
| 5 | Sản phẩm bị lỗi có thể đổi trả. | Sản phẩm bị lỗi có thể được hoàn trả. | cao | 0.0385 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là các cặp câu gần nghĩa vẫn có điểm rất thấp hoặc âm. Nguyên nhân là `_mock_embed` tạo vector từ hash của toàn bộ chuỗi, không phải embedding ngữ nghĩa; vì vậy chỉ nên dùng nó để kiểm tra tính xác định và logic xếp hạng, không dùng để kết luận chất lượng tiếng Việt.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Do `REPORT_NHOM.md` chưa có bộ câu hỏi chính thức, phần này dùng tạm 5 câu hỏi tự xây dựng từ hai tài liệu khởi động trong `data/k4_ecommerce/`. Chiến lược chạy là `SentenceChunker(max_sentences_per_chunk=2)` và `_mock_embed`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người mua cần làm gì khi yêu cầu đổi trả? | `k4-returns-policy::chunk_0`, chủ yếu là phần template metadata | 0.1705 | Không ở top-1 | Demo LLM nhận được context; chưa có LLM thật để sinh câu trả lời factual. |
| 2 | Người bán chịu trách nhiệm gì khi đăng bán sản phẩm? | `k4-seller-listing::chunk_0` | 0.1727 | Có | Demo LLM nhận được context liên quan. |
| 3 | Khi nào người mua cần kèm bằng chứng cho yêu cầu đổi trả? | `k4-returns-policy::chunk_1` | 0.1509 | Có | Demo LLM nhận được đoạn nêu hàng lỗi/không đúng mô tả. |
| 4 | Sản phẩm nào không được phép đăng bán? (`customer_role=seller`) | `k4-seller-listing::chunk_0` | 0.1557 | Chưa ở top-1 | Chunk liên quan nằm top-2; filter giúp loại tài liệu buyer. |
| 5 | Người bán phải làm gì sau khi nhận yêu cầu đổi trả? | `k4-returns-policy::chunk_2` | 0.1526 | Có | Demo LLM nhận được đoạn về phản hồi theo quy trình sàn. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

> Đây là benchmark tạm thời, chưa phải bộ 5 câu hỏi chính thức của nhóm. Các URL trong dữ liệu khởi động cũng là URL mẫu cần thay bằng nguồn công khai thật.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua phần cài đặt, tôi hiểu rõ hơn cách một hệ thống RAG nối các bước chunking, embedding, retrieval và prompt. Tôi cũng học được rằng metadata filter có thể tăng độ chính xác theo đối tượng, còn mock embedding chỉ phù hợp để kiểm thử kỹ thuật chứ không thể dùng để đánh giá semantic retrieval.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60 (tạm tính)** |
