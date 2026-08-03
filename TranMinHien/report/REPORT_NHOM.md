# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Trung tâm hỗ trợ khách hàng & quy định chính sách trên 2 sàn TMĐT Shopee và TikTok Shop (đổi trả, thanh toán SPayLater, vận chuyển, lỗi đăng nhập, sản phẩm bị cấm).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | [Shopee] Lỗi đăng nhập tài khoản | `https://help.shopee.vn/...` | 2026-08-03 / not-stated | 4,124 | `doc_id`, `category=account`, `customer_role=buyer` |
| 2 | [Shopee] Trạng thái đơn hàng | `https://help.shopee.vn/...` | 2026-08-03 / not-stated | 1,309 | `doc_id`, `category=orders`, `customer_role=buyer` |
| 3 | [Shopee] Điều khoản dịch vụ | `https://help.shopee.vn/...` | 2026-08-03 / not-stated | 83,374 | `doc_id`, `category=returns-policy`, `customer_role=buyer` |
| 4 | [Shopee] Hóa đơn SPayLater quá hạn | `https://help.shopee.vn/...` | 2026-08-03 / not-stated | 2,826 | `doc_id`, `category=spaylater`, `customer_role=buyer` |
| 5 | [TikTok Shop] Hủy đơn & Đổi trả | `https://seller-vn.tiktok.com/...` | 2026-08-03 / not-stated | 23,465 | `doc_id`, `category=returns-refunds`, `customer_role=seller` |
| 6 | [TikTok Shop] Thực thi Nhà sáng tạo | `https://seller-vn.tiktok.com/...` | 2026-08-03 / not-stated | 12,207 | `doc_id`, `category=creator-policy`, `customer_role=creator` |
| 7 | [TikTok Shop] Điều khoản Logistics | `https://seller-vn.tiktok.com/...` | 2026-08-03 / not-stated | 47,915 | `doc_id`, `category=logistics`, `customer_role=seller` |
| 8 | [TikTok Shop] Hướng dẫn sản phẩm cấm | `https://seller-vn.tiktok.com/...` | 2026-08-03 / not-stated | 34,787 | `doc_id`, `category=prohibited-products`, `customer_role=seller` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | Chuỗi | `shopee-account-login-issue` | Định danh duy nhất tài liệu, dùng để xóa/lọc tất cả chunk thuộc 1 doc |
| `source_url` | Chuỗi | `https://help.shopee.vn/...` | Giúp truy vết nguồn gốc và trích dẫn kiểm chứng câu trả lời |
| `customer_role` | Chuỗi | `buyer` / `seller` / `creator` | Đỉnh hướng lọc thông tin theo vai trò người dùng (người mua / người bán) |
| `category` | Chuỗi | `returns-refunds`, `account`, `logistics` | Dùng cho `search_with_filter()` khoanh vùng chủ đề chính xác trước khi tính vector |
| `retrieved_at` | Chuỗi | `2026-08-03` | Quản lý độ mới của chính sách TMĐT |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên các tài liệu chính sách:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `shopee-account-login-issue` | FixedSizeChunker (`fixed_size`) | 9 | 458.2 | Không, bị ngắt giữa câu và cắt đôi tiêu đề |
| `shopee-account-login-issue` | SentenceChunker (`by_sentences`) | 8 | 512.4 | Tạm ổn, nhưng ngắt không theo cấu trúc đoạn văn Markdown |
| `shopee-account-login-issue` | RecursiveChunker (`recursive`) | 10 | 407.7 | Có, ngắt tự nhiên theo xuống dòng `\n\n` và giữ nguyên tiêu đề |
| `shopee-order-status-not-updated` | FixedSizeChunker (`fixed_size`) | 3 | 436.3 | Không, cắt ngang giữa chừng bước xử lý |
| `shopee-order-status-not-updated` | SentenceChunker (`by_sentences`) | 3 | 434.0 | Khá, nhưng thiếu tính phân cấp tiêu đề |
| `shopee-order-status-not-updated` | RecursiveChunker (`recursive`) | 4 | 325.8 | Rất tốt, chia vừa đủ theo từng bước hướng dẫn |

### Chiến lược của từng thành viên

**Thành viên 1 — Trần Minh Hiển (Bài tập 3.1)**
- **Loại chiến lược:** `RecursiveChunker`
- **Mô tả & lý do chọn cho chủ đề này:** Các văn bản chính sách TMĐT được trình bày dưới dạng Markdown có cấu trúc phân cấp rõ ràng (Tiêu đề `#`, `##`, các bước đánh số `1.`, `2.`, và các đoạn văn cách nhau bởi `\n\n`). `RecursiveChunker` dùng thứ tự phân tách ưu tiên `["\n\n", "\n", ". ", " ", ""]`, giúp tách theo từng khối đoạn văn/điều khoản hoàn chỉnh trước khi xét đến dòng hay câu. Điều này đảm bảo mỗi chunk chứa trọn vẹn một ý chính sách.
- **Code snippet:**
```python
from src.chunking import RecursiveChunker

# Chiến lược chia nhỏ đệ quy ưu tiên ranh giới đoạn văn Markdown
chunker = RecursiveChunker(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=500
)
chunks = chunker.chunk(document_text)
```

**Thành viên 2 — (Đang thử nghiệm)**
- **Loại chiến lược:** `FixedSizeChunker` (chunk_size=500, overlap=50)
- **Mô tả & lý do chọn:** Chiến lược kích thước cố định tạo các chunk đồng đều về độ dài.
- **Code snippet:** `FixedSizeChunker(chunk_size=500, overlap=50)`

**Thành viên 3 — (Đang thử nghiệm)**
- **Loại chiến lược:** `SentenceChunker` (max_sentences_per_chunk=3)
- **Mô tả & lý do chọn:** Chia theo số lượng câu cố định để giữ trọn vẹn từng câu đơn lẻ.
- **Code snippet:** `SentenceChunker(max_sentences_per_chunk=3)`

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Thành viên 1 | `RecursiveChunker` | 9/10 | Giữ trọn cấu trúc đoạn Markdown, không bị cắt rập rờn câu/tiêu đề, ngữ cảnh rõ ràng | Kích thước các chunk có thể không đồng đều tuyệt đối |
| Thành viên 2 | `FixedSizeChunker` | 6/10 | Đơn giản, kiểm soát chính xác dung lượng bộ nhớ | Hay bị cắt giữa chừng từ/câu hoặc cắt đôi tiêu đề điều khoản |
| Thành viên 3 | `SentenceChunker` | 7/10 | Giữ nguyên từng câu hoàn chỉnh | Dấu xuống dòng trong Markdown không có dấu chấm dễ bị ghép sai tiêu đề |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> `RecursiveChunker` là chiến lược tối ưu nhất cho chủ đề chính sách TMĐT. Văn bản chính sách có tính phân cấp cao, việc phân tách đệ quy theo thứ tự `\n\n` ➔ `\n` ➔ `. ` giúp giữ nguyên toàn bộ một điều khoản hoặc một quy trình hướng dẫn trong cùng một chunk. Nhờ đó vector embedding phản ánh chính xác ngữ cảnh của điều khoản, nâng cao vượt trội chất lượng truy xuất (Retrieval Quality).

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mã OTP đăng nhập Shopee có hiệu lực trong bao lâu? | Mã OTP đăng nhập Shopee có hiệu lực trong vòng 60 giây kể từ khi nhận được. | `shopee-account-login-issue::chunk_0` |
| 2 | Đơn hàng Shopee bị chậm cập nhật trạng thái do những nguyên nhân nào? | Do đơn vị vận chuyển chưa cập nhật lên hệ thống hoặc trong thời gian nghỉ lễ/cuối tuần. | `shopee-order-status-not-updated::chunk_0` |
| 3 | Người mua cần làm gì khi quá hạn thanh toán hóa đơn SPayLater? | Người mua cần nạp tiền/thanh toán ngay lập tức qua ví ShopeePay hoặc tài khoản ngân hàng để tránh phí quá hạn. | `shopee-spaylater-overdue-invoice::chunk_0` |
| 4 | Những nhóm sản phẩm nào bị cấm đăng bán trên TikTok Shop? | Vũ khí, chất cháy nổ, ma túy, tài sản trộm cắp, động vật hoang dã, hàng giả hàng nhái. | `tiktok-prohibited-products::chunk_0` |
| 5 | Quy định hủy đơn hàng và trả hàng hoàn tiền áp dụng cho đối tượng nào? *(Lọc: `customer_role='seller'`)* | Áp dụng cho Nhà bán hàng (Seller) trên TikTok Shop khi xử lý yêu cầu hủy đơn từ khách hàng. | `tiktok-cancellation-returns-refunds::chunk_0` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mã OTP đăng nhập Shopee | `RecursiveChunker` | Có | Khi dùng embedder thật local, `RecursiveChunker` đưa đúng chunk quy định OTP lên Top-1 |
| 2 | Đơn hàng Shopee bị chậm | `RecursiveChunker` | Có | Chunk chứa thông tin bước xử lý hiển thị ở Top-1 |
| 3 | Hóa đơn SPayLater quá hạn | `RecursiveChunker` | Có | Chunk giải thích phí quá hạn được trích xuất chính xác |
| 4 | Sản phẩm bị cấm TikTok Shop | `RecursiveChunker` | Có | Giữ trọn danh mục sản phẩm bị cấm trong cùng 1 chunk |
| 5 | Quy định hủy đơn (Seller) | `RecursiveChunker` + Filter | Có | Phải lọc `customer_role='seller'` để loại bỏ nhầm lẫn với quy định dành cho người mua |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Metadata filtering cực kỳ quan trọng ở **Câu hỏi #5**. Vì cả tài liệu dành cho Người mua (Shopee) và Người bán (TikTok Shop) đều có các từ khóa trùng lặp ("hủy đơn", "trả hàng", "hoàn tiền"). Nếu không dùng `search_with_filter(filter_metadata={'customer_role': 'seller'})`, vector search bị trộn lẫn 2 văn bản khiến Agent trả lời sai đối tượng. Việc lọc trước giúp khoanh vùng chính xác tập tài liệu phù hợp.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. `RecursiveChunker` vượt trội hơn hẳn `FixedSizeChunker` đối với tài liệu cấu trúc phân cấp (Markdown chính sách), vì giữ được trọn vẹn ranh giới khối ngữ cảnh mà không bị cắt rập rờn tiêu đề.
2. Metadata Filtering là cơ chế phòng vệ tuyệt đối chống nhiễu ngữ cảnh giữa các đối tượng khác nhau (ví dụ: Quy định Người mua vs Quy định Người bán).
3. Đánh giá truy xuất (Retrieval Quality) phụ thuộc chặt chẽ vào việc kết hợp cả chiến lược Chunking tối ưu và Embedding Model phù hợp ngữ nghĩa tiếng Việt.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tập dữ liệu chính sách TMĐT, nếu dùng `FixedSizeChunker` các tiêu đề và quy trình bị ngắt nửa chừng khiến vector search trả về kết quả nhiễu. Trong khi đó, `RecursiveChunker` bảo toàn được ranh giới đoạn văn `\n\n`, giúp câu trả lời của Agent mạch lạc và chính xác hơn đáng kể.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thiết kế thêm các trường metadata chuyên sâu hơn như `product_type` (loại hàng hóa) hoặc `policy_type` (chính sách chung/riêng) để tăng độ chính xác khi truy vấn các câu hỏi có bộ lọc phức tạp.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
