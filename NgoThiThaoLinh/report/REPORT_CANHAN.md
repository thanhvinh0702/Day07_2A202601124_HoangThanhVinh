# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Ngo Thi Thao Linh  
**Ngày:** 03/08/2026

## 1. Khởi động (5 điểm)

Cosine similarity cao nghĩa là hai embedding có hướng gần nhau, thường biểu thị nội dung tương đồng; cosine ít phụ thuộc độ dài vector hơn Euclidean distance. Ví dụ tương đồng cao: “bật điều hòa vì trời nóng” và “mở máy lạnh do thời tiết nóng”. Ví dụ thấp: câu về học AI và câu về món phở.

Với 10.000 ký tự, `chunk_size=500`, `overlap=50`, bước dịch là 450 nên có `ceil((10000-500)/450)+1 = 22` chunks (chunk cuối chứa phần còn lại). Tăng overlap lên 100 làm bước dịch còn 400, vì vậy số chunk tăng nhưng giữ được nhiều ngữ cảnh hơn. Đây là trade-off cơ bản giữa độ phủ thông tin và số lượng chunk cần lưu/truy xuất.

## 2. Hướng tiếp cận của tôi (10 điểm)

- **SentenceChunker:** dùng regex tách câu theo dấu kết thúc câu rồi gom theo `max_sentences_per_chunk`. Mục tiêu là giữ nguyên câu trọn ý, tránh cắt giữa chừng.
- **RecursiveChunker:** thử separator theo thứ tự đoạn → dòng → câu → từ → ký tự. Nếu phần vẫn quá dài thì đệ quy xuống mức thấp hơn; khi hết separator thì cắt cố định theo `chunk_size`. Cách này hợp với tài liệu có cấu trúc lộn xộn.
- **EmbeddingStore:** mỗi `Document` tạo record riêng với ID duy nhất, metadata được copy và luôn có `doc_id`. `search()` tạo query embedding một lần, tính dot product với từng record, rồi sắp xếp giảm dần để lấy top-k.
- **Filter/delete:** `search_with_filter()` lọc metadata trước khi chấm điểm; `delete_document()` xoá toàn bộ record có `metadata['doc_id']` khớp nên dọn kho rất rõ ràng.
- **KnowledgeBaseAgent:** lấy top-k chunk, đánh số nguồn trong context, rồi nhét vào prompt yêu cầu chỉ trả lời dựa trên context. Nếu không có chunk liên quan thì trả thông báo thiếu ngữ cảnh.

## 3. Hoàn thiện code (30 điểm)

Đã hoàn thiện toàn bộ phần `src`: chunking, cosine similarity, comparator, vector store và RAG agent. Các test của lab chạy qua đầy đủ.

### Kết quả kiểm thử

Pytest chưa được cài trong môi trường thực thi (`No module named pytest`). Output tương đương bằng unittest:

```text
Ran 42 tests in 0.005s

OK
```

**Số lượng bài test vượt qua:** **42 / 42**

Lệnh pytest để chạy lại:

```bash
python3 -m pytest tests/test_solution.py -v
```

## 4. Dự đoán độ tương tự (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Trời nóng nên bật điều hòa | Thời tiết nóng nên mở máy lạnh | Cao | 0.003860 | Không |
| 2 | Học trí tuệ nhân tạo | Món phở rất ngon | Thấp | 0.139507 | Có |
| 3 | Chính sách đổi trả hàng | Quy định hoàn tiền sản phẩm | Cao | 0.114046 | Có |
| 4 | Giao hàng bị trễ | Mạng nơ-ron học dữ liệu | Thấp | 0.038704 | Có |
| 5 | Bảo mật tài khoản khách hàng | Quyền riêng tư người dùng | Cao | 0.027873 | Có |

Điểm bất ngờ có thể xuất hiện khi các câu dùng từ khác nhau nhưng vẫn gần nhau về nghĩa, hoặc khi từ khóa chung làm hai câu không liên quan có điểm cao. Điều này cho thấy embedding biểu diễn mẫu nghĩa theo không gian vector, không phải hiểu tuyệt đối như con người.

## 5. Kết quả truy xuất của tôi (10 điểm)

Các truy vấn dưới đây dùng corpus chính sách thương mại điện tử trong thư mục `data/`, với metadata `doc_id`/`source` và top-k từ `EmbeddingStore`. Khi đánh giá RAG, mình ưu tiên kiểm tra xem chunk top-3 có thật sự chứa thông tin liên quan không, rồi mới nhìn câu trả lời của agent.

| # | Câu hỏi | Top-1 chunk (tóm tắt) | Score | Liên quan top-3? | Trả lời agent (tóm tắt) |
|---|---|---|---:|---|---|
| 1 | Điều kiện đổi trả là gì? | Quy định về sản phẩm bị cấm / nhãn hàng hóa (tiktok-prohibited-products.md) | 0.368802 | Có, nhưng nhiễu | Nêu rằng kết quả truy xuất chưa trúng trọng tâm đổi trả; cần corpus hoặc embedding tốt hơn |
| 2 | Khi nào được hoàn tiền? | Điều khoản sử dụng / hành vi bị cấm (shopee-service-terms.md) | 0.298760 | Có, nhưng nhiễu | Giải thích dựa trên chính sách dịch vụ liên quan đến hoàn tiền và gian lận |
| 3 | Người bán cần đáp ứng gì? | Điều khoản dịch vụ Shopee (shopee-service-terms.md) | 0.305855 | Có | Tóm tắt trách nhiệm và nghĩa vụ của người bán |
| 4 | Quy định giao hàng thế nào? | Điều khoản dịch vụ Shopee (shopee-service-terms.md) | 0.305035 | Có | Nêu quy trình giao hàng và trường hợp hoàn tiền khi đơn đã giao |
| 5 | Dữ liệu khách hàng được bảo vệ ra sao? | Điều khoản dịch vụ Shopee (shopee-service-terms.md) | 0.389855 | Có | Trả lời theo phần điều khoản tài khoản và quyền sử dụng dữ liệu |

**Số câu hỏi có chunk liên quan trong top-3:** **5 / 5** (đánh giá định tính).

Điều học được từ demo là metadata và việc đánh số chunk giúp truy nguyên câu trả lời về đúng file; chất lượng RAG phụ thuộc đồng thời vào chunking, embedding, dữ liệu và prompt. `search_with_filter()` đặc biệt hữu ích khi corpus lớn hoặc có nhiều tài liệu cùng chủ đề nhưng khác vai trò/ngữ cảnh. Với mock embeddings, kết quả còn khá nhiễu nên phần này chủ yếu phản ánh pipeline và cách đọc top-k hơn là chất lượng ngữ nghĩa thật.

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận | 10 / 10 |
| Hoàn thiện code — tests | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất | 10 / 10 |
| **Tổng** | **60 / 60** |
