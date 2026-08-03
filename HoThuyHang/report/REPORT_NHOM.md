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
> *1 câu — ví dụ: đổi trả + điều kiện người bán.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Dạng | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Tài liệu + chunk kỳ vọng |
|---|---|-------|-------------------------------|--------------------------|
| 1 | Số liệu | Khách hàng có bao nhiêu ngày để gửi yêu cầu trả hàng/hoàn tiền sau khi đơn được cập nhật là “Đã giao hàng”? | Khách hàng có thể gửi yêu cầu trong vòng **15 ngày** kể từ khi đơn hàng được cập nhật trạng thái “Đã giao hàng”. | `tiktok-cancellation-returns-refunds`, mục 4.1, chunk chứa câu “trong vòng 15 ngày”. |
| 2 | Điều kiện | Nhà bán hàng có thể hủy đơn hàng TikTok Shop đến thời điểm nào? | Nhà bán hàng có thể hủy đơn **bất kỳ lúc nào trước khi đơn chuyển sang “Đã vận chuyển - Đang vận chuyển”**; việc này ảnh hưởng đến Tỷ lệ hủy do lỗi Người bán. | `tiktok-cancellation-returns-refunds`, mục 3.1, chunk chứa điều kiện hủy bởi Người bán. |
| 3 | Quy trình | Nếu nhà bán hàng từ chối yêu cầu trả hàng/hoàn tiền, khách hàng cần làm gì và trong bao lâu? | Khách hàng có thể gửi yêu cầu lần thứ hai **trong vòng 48 giờ** sau khi bị từ chối. Nếu không gửi lại trong thời hạn này, nền tảng sẽ đóng yêu cầu. | `tiktok-cancellation-returns-refunds`, mục 4.1, chunk chứa quy trình gửi lại yêu cầu. |
| 4 | Liệt kê (bắt buộc lọc) | Khi vi phạm chính sách, nền tảng có thể áp dụng những biện pháp nào đối với nhà sáng tạo? | Với tài liệu dành cho `customer_role=creator`, các biện pháp gồm: **gỡ nội dung**, **hạn chế quyền truy cập tính năng sản phẩm**, **tạm dừng kiếm tiền/hoa hồng**; tùy mức độ còn có thể đình chỉ video/LIVE hoặc xóa tài khoản. | `tiktok-creator-enforcement-policy`, mục “What Enforcement Can Look Like”, chunk chứa danh sách biện pháp. **Bắt buộc filter:** `customer_role=creator`. |
| 5 | Ngoại lệ | Đơn có nhiều sản phẩm và dùng voucher miễn phí vận chuyển có được hủy một phần không? | **Không.** Khách hàng phải hủy toàn bộ đơn. Tuy nhiên, sản phẩm đã sẵn sàng vận chuyển cần người bán chấp nhận, còn sản phẩm chưa sẵn sàng vận chuyển thì yêu cầu hủy được tự động phê duyệt. | `tiktok-cancellation-returns-refunds`, mục 3.2.1, chunk chứa ngoại lệ đơn nhiều sản phẩm + voucher. |

**Quy tắc cố định benchmark:** Đây là đúng 5 query dùng chung cho mọi strategy; không thay đổi câu hỏi sau khi đã chạy thử. Query 4 phải chạy với bộ lọc `customer_role=creator`, vì nếu không lọc, các tài liệu dành cho `seller` cũng có từ vựng “vi phạm/chế tài” và retrieval có thể trả lời sai đối tượng.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
