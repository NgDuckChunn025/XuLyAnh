# Hướng dẫn báo cáo tiến độ — tuần bắt đầu 16/11/2026

Mục tiêu: trình bày khoảng 6–8 phút, chứng minh phần đã làm được, hiểu kết quả và có kế hoạch tiếp theo. Đây là hướng dẫn nội dung để đưa vào slide, chưa phải file PowerPoint. Điều chỉnh theo thời lượng và biểu mẫu giảng viên yêu cầu.

## 1. Kết quả đã kiểm tra

- Đã tự cài đặt ISODATA bằng NumPy, đủ gán nhãn, cập nhật tâm, loại cụm nhỏ, tách và gộp.
- Có pipeline ảnh RGB/Lab/gray, tùy chọn XY, dựng ảnh màu theo tâm cụm.
- Có K-means tự viết để đối chiếu; demo mới hiển thị cả K-means cùng số cụm cuối.
- Đã sửa SSE cuối, bổ sung kiểm tra đầu vào và tránh báo hội tụ chỉ vì vòng cuối bỏ qua tách/gộp.
- 5 test hồi quy đều đạt; 4 tình huống 2D đều đạt. Đây là các trường hợp đã kiểm tra, không phải chứng minh thuật toán đúng với mọi dữ liệu.
- Đã chạy 5 ảnh x 2 không gian màu, mỗi cấu hình gồm ISODATA, K-means K=5 và K-means cùng K cuối: tổng 30 dòng kết quả.

Nguồn số liệu lần chạy hiện tại: [RESULTS.md](../results/progress/20261112_004755_179432/RESULTS.md), [summary.csv](../results/progress/20261112_004755_179432/summary.csv), [config.json](../results/progress/20261112_004755_179432/config.json).

## 2. Dàn ý 6 slide và lời nói gợi ý

### Slide 1 — Bài toán và mục tiêu (40 giây)

Nội dung trên slide:
- Đề tài: Phân cụm ảnh bằng thuật toán ISODATA.
- Đầu vào: ảnh; mỗi pixel được biểu diễn bằng vector đặc trưng.
- Đầu ra: nhãn cụm và ảnh thay màu pixel bằng màu tâm cụm.
- Mục tiêu: khảo sát cơ chế điều chỉnh số cụm và so sánh với K-means.

Lời nói: “Em nghiên cứu phân cụm các pixel có đặc trưng gần nhau. ISODATA cho phép thay đổi số cụm qua thao tác loại, tách và gộp. Hiện em tập trung vào cài đặt và kiểm chứng cơ chế, sau đó thực nghiệm trên ảnh thật.”

### Slide 2 — Ý tưởng thuật toán (60 giây)

Vẽ sơ đồ bằng các hộp: Khởi tạo tâm → Gán pixel → Loại cụm nhỏ → Cập nhật tâm → Chọn tách/gộp → Kiểm tra dừng → Gán nhãn cuối.

- Loại: ít hơn theta_N pixel; pixel được gán lại, không bị xóa.
- Tách: độ lệch chuẩn lớn và thỏa điều kiện kích thước/phân tán hoặc số cụm ít.
- Gộp: hai tâm gần hơn theta_c; tâm mới là trung bình có trọng số số mẫu.
- K là định hướng, init_k là số tâm ban đầu; không bảo đảm tìm đúng số đối tượng.

Lời nói: “Sau khi cập nhật tâm, thuật toán quyết định tách hoặc gộp theo số cụm hiện tại và vòng lặp. Các ngưỡng chi phối kết quả nên cần khảo sát; không thể nói ISODATA hoàn toàn không cần tham số.”

### Slide 3 — Những phần đã hoàn thành (45 giây)

Đưa pipeline: Ảnh → Thu nhỏ → RGB/Lab → Ma trận N×d → ISODATA/K-means → Nhãn → Ảnh và chỉ số.

Liệt kê ngắn: lõi NumPy; test 2D; ảnh thật; batch CSV/PNG/JSON. Không chụp cả màn hình code hoặc liệt kê mọi hàm.

### Slide 4 — Kiểm chứng trên dữ liệu 2D (60 giây)

Dùng [biểu đồ số cụm](../results/test2d/n_clusters_curve.png) và chọn thêm [hình tách cụm](../results/test2d/test3_split.png).

| Tình huống | Kết quả thực tế |
|---|---|
| Tắt tách/gộp | SSE ISODATA và K-means cùng khoảng 729,56 |
| Khởi tạo 10 tâm | Về 4 cụm sau 4 vòng, có sự kiện gộp |
| Khởi tạo 2 tâm | Lên 4 cụm sau 5 vòng, có sự kiện tách |
| Thêm 6 điểm nhiễu, khởi tạo 12 tâm | Có loại cụm nhỏ, kết thúc 4 cụm |

Lời nói: “Dữ liệu giả lập có bốn nhóm đã biết giúp kiểm tra riêng cơ chế. Kết quả này cho thấy các tình huống kiểm thử hoạt động như mong đợi; chưa thay thế đánh giá trên ảnh thật.”

### Slide 5 — Kết quả bước đầu trên ảnh thật (90 giây)

Dùng [ảnh phong cảnh Lab](../results/progress/20261112_004755_179432/phongcanh_lab_compare.png). Có thể tách hình thành hai slide nếu chữ quá nhỏ: một slide ảnh so sánh, một slide bảng kết quả.

Cấu hình: cạnh dài tối đa 200 pixel, K=5, init_k=10, theta_N=max(10, 0,2% số pixel lấy phần nguyên), theta_S=25, theta_c=30, L=2, tối đa 50 vòng, seed=0; không thêm XY.

| Ảnh / màu | K cuối | Vòng lặp | Trạng thái |
|---|---:|---:|---|
| Phong cảnh / Lab | 7 | 18 | Hội tụ |
| Logo / RGB | 10 | 16 | Hội tụ |
| Vệ tinh / Lab | 2 | 22 | Hội tụ |
| Chân dung / Lab | 4 | 50 | Chưa hội tụ trong giới hạn |

Lời nói: “Trong 10 cấu hình ISODATA, 8 cấu hình hội tụ và 2 cấu hình chân dung chạm giới hạn 50 vòng. Phong cảnh Lab từ 10 tâm về 7 cụm, SSE khoảng 9,65 triệu. K-means cùng 7 cụm đạt khoảng 9,63 triệu, thấp hơn một chút. Vì vậy hiện chưa có căn cứ kết luận ISODATA tốt hơn K-means về SSE; kết quả thể hiện cơ chế điều chỉnh số cụm và sự phụ thuộc dữ liệu.”

Không so SSE RGB với Lab để kết luận Lab tốt hơn. Không gọi Silhouette là accuracy. Đây là một seed, chưa có độ lệch chuẩn hoặc nhãn chuẩn.

### Slide 6 — Hạn chế và kế hoạch (60 giây)

Đã có: thuật toán, kiểm thử, demo và bảng kết quả bước đầu.

Còn thiếu:
- Một seed và bộ ảnh nhỏ; chưa kết luận độ ổn định.
- Chưa khảo sát hệ thống các ngưỡng; cùng ngưỡng RGB/Lab không có nghĩa cùng ý nghĩa hình học.
- Chưa có nhãn chuẩn để đánh giá phân đoạn; vùng cùng màu có thể không cùng đối tượng.
- Một số cấu hình chưa hội tụ trong giới hạn.

Kế hoạch tiếp theo: chạy seed 0–4; thay từng nhóm tham số trong khi giữ phần còn lại; tổng hợp trung bình/độ lệch chuẩn, số cụm và trạng thái hội tụ; bổ sung nguồn ảnh và tài liệu tham khảo; hoàn thiện báo cáo.

Lời kết: “Phần cài đặt và kiểm chứng ban đầu đã hoàn thành. Giai đoạn tiếp theo em tập trung vào thực nghiệm để xác định ảnh hưởng của tham số và phạm vi hiệu quả của phương pháp.”

## 3. Demo trực tiếp khoảng 1 phút

Mở terminal ở thư mục gốc dự án:

```powershell
.\venv\Scripts\python.exe run_isodata.py images/phongcanh.jpg --space lab -k 5 --init-k 10 -I 50 --verbose
```

Giải thích log số cụm/thao tác, trạng thái hội tụ, SSE của K-means cùng K. Script lưu PNG, không tự mở cửa sổ. Mở trước ảnh so sánh đã lưu để chuyển sang ngay sau log. Có thể dùng hình batch đã liên kết ở trên; cấu hình này giống nhau.

Không cần chạy toàn bộ batch trong lúc báo cáo. Giữ sẵn ảnh và bảng số liệu để trình bày nếu máy chiếu hoặc terminal gặp lỗi. Luyện một lần từ đầu đến cuối trên đúng máy mang đi.

## 4. Các câu hỏi dễ gặp

**ISODATA khác K-means ở đâu?** K-means giữ số tâm đã chọn; ISODATA bổ sung loại/tách/gộp, nên số cụm cuối có thể thay đổi.

**Vẫn nhập K thì tự động ở đâu?** K là định hướng điều khiển thao tác, không ép số cụm cuối. Các ngưỡng và dữ liệu cùng ảnh hưởng kết quả.

**Tại sao chọn 25 và 30?** Đây là cấu hình thử nghiệm ban đầu trên đặc trưng mã hóa 8-bit, chưa chứng minh tối ưu; bước tiếp theo là khảo sát độ nhạy. Không nói đã tối ưu nếu chưa thực hiện.

**Số cụm không đổi đã hội tụ chưa?** Chưa đủ. Cần tâm dịch chuyển nhỏ và hai vòng liên tiếp không thay đổi cấu trúc. Vòng cuối bỏ qua tách/gộp không được dùng làm bằng chứng hội tụ.

**Tại sao ISODATA không có SSE tốt hơn?** Nó điều chỉnh cấu trúc cụm và vẫn phụ thuộc khởi tạo/ngưỡng. Khi cố định cùng K, K-means có thể đạt SSE thấp hơn. Chưa có kết luận ưu thế tổng quát từ lần chạy này.

**Có loại bỏ nhiễu khỏi ảnh không?** Không xóa pixel; cụm nhỏ bị bỏ và các pixel được gán vào các tâm còn lại.

**Ảnh X-quang có chứng minh phân đoạn bệnh không?** Không. Ở đây chỉ minh họa phân cụm cường độ/màu, không có nhãn bệnh hay đánh giá chẩn đoán.

**Silhouette phản ánh điều gì?** Độ chặt trong cụm so với mức tách khỏi cụm khác trong không gian đặc trưng; giá trị cao hơn không tự chứng minh vùng đối tượng đúng.

## 5. Việc bạn cần làm trước buổi báo cáo

1. Chuyển nội dung trên thành 6–7 slide; bổ sung tên, lớp, nhóm và giảng viên.
2. Dùng đúng hình và số liệu của cùng lần chạy; đừng trộn ảnh kết quả cũ với bảng mới.
3. Luyện giải thích K/init_k, ba ngưỡng và sự khác nhau giữa hết vòng với hội tụ.
4. Thử lệnh demo bằng `venv`, mở sẵn PNG và giữ bản slide offline.
5. Điền nguồn ảnh thực tế bạn đã lấy; bổ sung tài liệu thuật toán theo tài liệu môn học và biến thể đang cài đặt. Không tự gán nguồn chưa xác minh.
