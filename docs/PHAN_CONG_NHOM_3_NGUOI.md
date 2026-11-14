# Phân công nhóm 3 người và chuẩn bị báo cáo tiến độ

Mốc chuẩn bị: thứ Bảy 14/11 và Chủ nhật 15/11/2026, hướng tới buổi báo cáo đầu tuần bắt đầu 16/11. Nếu lịch thầy khác, giữ thứ tự công việc và dịch các mốc. Chưa có tên hai thành viên nên dùng TV2 và TV3 để bạn thay tên.

Đây là phân công đề xuất từ thời điểm hiện tại, không phải xác nhận ai đã làm những phần code có sẵn. Khi báo cáo đóng góp, chỉ ghi công việc từng người thực sự hoàn thành và kiểm tra.

## 1. Phân vai và sản phẩm bàn giao

| Người | Trách nhiệm chính | Sản phẩm trước báo cáo | Tiêu chí hoàn thành |
|---|---|---|---|
| Bạn — trưởng nhóm, báo cáo chính | Nắm toàn bộ luồng thuật toán; kiểm tra kết quả; tổng hợp nội dung; demo và vấn đáp | Dàn nói 6–8 phút; ví dụ tính tay; bản slide cuối; danh sách hạn chế | Tự giải thích được công thức → code → kết quả; demo không cần người khác thao tác hộ |
| TV2 — thuật toán và kiểm thử | Đọc sâu các hàm trong `isodata.py`, đối chiếu tài liệu, xác nhận các điều kiện tách/gộp và dừng | Bảng công thức–hàm; log chạy test; một trang giải thích AND/OR khi tách; ghi rõ biến thể so với tài liệu | Chạy được test; tự tính ví dụ {0,2,8,10}; trả lời được vì sao gộp dùng trọng số |
| TV3 — thực nghiệm và minh họa | Kiểm tra nguồn ảnh; đọc cấu hình/seed; tổ chức hình và bảng; chuẩn bị phần slide thực nghiệm | Bảng nguồn 5 ảnh; 2–3 hình minh họa; bảng tham số; 3 nhận xét có số liệu và 2 hạn chế | Mỗi nhận xét truy được về file kết quả; phân biệt hội tụ/hết vòng, không gọi Silhouette là accuracy |

Bạn không cần làm thay hai bạn còn lại. Mỗi bạn phụ trách phải dạy lại phần mình trong 10 phút cho bạn; bạn hỏi cho đến khi có thể diễn đạt lại bằng lời của mình.

## 2. Công việc cụ thể

### Bạn — trưởng nhóm

1. Đọc [Hiểu ISODATA](HIEU_ISODATA_VA_VAN_DAP.md) theo thứ tự mục 1 → 8 → 5 → 6 → 9 → 11. Hiểu ví dụ số trước khi học mọi điều kiện.
2. Chạy `demo_formulas.py`; lấy giấy tự tính tâm, D, sigma, SSE và hai tâm tách. Đóng tài liệu rồi giải thích lại.
3. Đọc một hàng cấu hình cơ sở trong kết quả mới, chỉ ra K=5 khác init_k=10 và K cuối=7/8 ở đâu.
4. Tổng hợp slide từ [hướng dẫn báo cáo](BAO_CAO_TIEN_DO.md). Thêm một slide độ nhạy, hoặc thay bảng dài bằng 3 hàng tiêu biểu để giữ thời lượng.
5. Duyệt số liệu/nguồn trước khi đưa vào slide. Chốt nội dung, tránh sửa thuật toán sát giờ báo cáo nếu chưa kiểm tra lại.

### TV2 — thuật toán

Các lệnh cần chạy từ thư mục gốc:

```powershell
.\venv\Scripts\python.exe -m unittest test_isodata -v
.\venv\Scripts\python.exe test_2d.py
.\venv\Scripts\python.exe demo_formulas.py
```

Đọc `assign`, `update_centers`, `cluster_stats`, `split_clusters`, `merge_clusters`, `isodata`. Bàn giao log dạng text kèm câu giải thích mỗi test kiểm tra điều gì. Đánh dấu “chưa rõ” nếu có điểm chưa hiểu thay vì khẳng định đã kiểm chứng.

Đối chiếu nguồn ở cuối tài liệu học; lưu tên tài liệu, URL, ngày truy cập và khác biệt với code. Không lấy tên một giáo trình làm nguồn chung nếu chưa đối chiếu được nội dung liên quan.

### TV3 — thực nghiệm

1. Dùng bộ batch trước và khảo sát mới đã có; không cần chạy lại mọi thứ nếu chỉ làm slide.
2. Chọn hình phong cảnh Lab để so sánh cùng K, hình tách/gộp 2D để minh họa cơ chế, hình độ nhạy để nói về tham số.
3. Ghi nguồn ảnh đúng thực tế: tên ảnh, URL hoặc người cung cấp, ngày lấy, mô tả. Chưa tìm thấy nguồn thì ghi “chưa xác minh”, không đoán.
4. Nếu còn thời gian, chạy thêm cùng khảo sát trên logo để xem nhận xét có còn đúng. Đây là việc tùy chọn, chỉ đưa vào báo cáo khi đọc xong kết quả:

```powershell
.\venv\Scripts\python.exe run_sensitivity.py --image images/logo.jpg --space lab --seeds 0 1 2
```

Mỗi lần sinh thư mục kết quả mới. Bàn giao chính xác đường dẫn và cấu hình, không trộn số liệu của hai lần chạy. Đừng nói “đã khảo sát 5 ảnh nhiều seed” khi hiện mới có một ảnh trong khảo sát nhiều seed.

## 3. Lịch phối hợp gọn

| Mốc | Công việc | Người chịu trách nhiệm |
|---|---|---|
| Thứ Bảy 14/11 | Chia vai, đọc tài liệu; trưởng nhóm làm ví dụ tay; TV2 chạy test; TV3 gom nguồn và hình | Cả nhóm |
| Chủ nhật 15/11 trước 12:00 | TV2 và TV3 bàn giao bản đầu, mỗi người giải thích lại phần mình | TV2, TV3; bạn kiểm tra |
| Chủ nhật trước 17:00 | Chốt 6–7 slide, kiểm tra một lượt số liệu và đường dẫn | Bạn tổng hợp, hai bạn đối chiếu |
| Chủ nhật 20:00–20:30 | Tập báo cáo và vấn đáp chéo; sửa các chỗ chưa hiểu | Cả nhóm |
| Trước buổi báo cáo 30 phút | Kiểm tra máy, terminal, ảnh offline, slide và lệnh demo | Bạn; TV3 giữ bản dự phòng |

## 4. Buổi tập vấn đáp 30 phút

- 8 phút: bạn trình bày như trước thầy, không bị ngắt.
- 7 phút: TV2 hỏi công thức: vì sao trung bình, sigma khác D thế nào, điều kiện tách, tâm gộp, SSE có luôn giảm không.
- 7 phút: TV3 hỏi kết quả: chọn tham số ra sao, cùng K để làm gì, kết quả nào chưa hội tụ, nhiều seed chứng minh gì/chưa chứng minh gì.
- 8 phút: bạn nói lại các câu vừa trả lời chưa rõ; sửa nội dung slide tương ứng.

Tiêu chí bạn sẵn sàng: giải được ví dụ bốn điểm không nhìn tài liệu; chỉ được hàm tương ứng mỗi bước; đọc được một bảng kết quả; nêu được ít nhất ba hạn chế; nói rõ công việc tiếp theo có thể kiểm chứng.

## 5. Quy tắc làm việc để tránh lặp lỗi Git

Trước khi làm, mỗi người đồng bộ nhánh của mình. Chia phạm vi file: TV2 phần test/tài liệu thuật toán; TV3 hình và phần thực nghiệm; bạn README và tài liệu tổng hợp. Hạn chế cùng sửa một file trong cùng thời điểm. Dùng nhánh riêng cho các thay đổi và để bạn duyệt/tích hợp. Không sửa trực tiếp README trên GitHub trong lúc một người đang chỉnh và rebase ở máy.

Nhóm tự ghi lại người thực hiện, file thay đổi, lệnh kiểm tra và kết quả. Các công cụ hỗ trợ tạo code/tài liệu không thay thế việc từng thành viên phải chạy, hiểu và chịu trách nhiệm về phần được nhận.
