# ISODATA Studio — hướng dẫn demo web

## Mở ứng dụng

Tại thư mục gốc dự án, chạy trong PowerShell:

```powershell
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.address=127.0.0.1 --server.port=8501
```

Mở **http://127.0.0.1:8501**. Giữ terminal đang chạy; Ctrl+C để dừng. Có thể chạy `./run_web.ps1` nếu chính sách PowerShell trên máy cho phép chạy script. Trên máy khác, tạo venv và cài `requirements.txt` theo README trước.

Đây là app chạy trên máy bạn; không cần tài khoản hay dịch vụ AI. Server chưa được triển khai lên Internet. Sau khi cài thư viện, xử lý ảnh không cần Internet; một số biểu tượng của giao diện có thể phụ thuộc tài nguyên font của trình duyệt.

## Các thao tác

1. Lần mở đầu hiển thị kết quả ảnh phong cảnh mẫu với cấu hình mặc định.
2. Chọn **Tải ảnh lên** và chọn/kéo thả PNG, JPG hoặc WEBP; hoặc chọn ảnh khác trong bộ ảnh mẫu.
3. Chọn Lab/RGB/Xám, K; mở **Tham số nâng cao** nếu muốn thay ngưỡng tách/gộp, số tâm ban đầu, seed, kích thước hoặc XY.
4. Bấm **Phân cụm ảnh**. Khi thay ảnh hoặc tham số, kết quả cũ được ẩn để không nhầm với cấu hình mới.
5. Trong **So sánh ảnh**, chuyển ISODATA/K-means để xem đầu ra cạnh ảnh đầu vào. K-means dùng cùng số tâm cuối của ISODATA.
6. Trong **Quá trình phân cụm**, xem số cụm, SSE và nhật ký từng vòng.
7. Trong **Hiểu thuật toán**, xem ý nghĩa các thao tác và công thức trung bình/SSE.
8. **Tải ảnh kết quả** xuất PNG của phương pháp đang chọn; **Tải thông số ISODATA** luôn xuất JSON của ISODATA.

## Kịch bản demo 2 phút

- 20 giây: chỉ ảnh gốc và ảnh ISODATA, giải thích màu đại diện của từng cụm.
- 30 giây: mở ngưỡng gộp, tăng từ 30 lên 50, bấm chạy lại; đọc số cụm thực tế, không hứa trước rằng mọi ảnh đều giảm K.
- 30 giây: mở biểu đồ, chỉ vòng có sự kiện gộp/tách. Giải thích số cụm ổn định khác với hội tụ.
- 20 giây: chuyển sang K-means cùng K, nói rõ SSE chỉ là sai số đặc trưng, không phải độ chính xác nhận diện vật thể.
- 20 giây: tải PNG và JSON để lưu kết quả. Chuẩn bị ảnh kết quả offline dự phòng.

## Phạm vi và cách đọc số liệu

- File tối đa 12 MB, tối đa 20 triệu pixel trước khi thu nhỏ. Ảnh hỏng được báo lỗi. Ảnh có độ trong suốt được ghép nền trắng; hướng EXIF được áp dụng.
- Cạnh xử lý tối đa mặc định 240 pixel, tùy chỉnh 120–400. Ảnh tải về có kích thước xử lý, không phải độ phân giải file gốc.
- Web dùng Pillow/Lanczos và xử lý EXIF/alpha, trong khi CLI cũ dùng OpenCV/INTER_AREA. Do đó số liệu web có thể khác bảng batch cũ, kể cả khi chọn cùng kích thước. Khi báo cáo dùng JSON của đúng lần chạy web.
- θN = max(1, int(tỷ lệ phần trăm × tổng pixel / 100)). ISODATA dùng tol=0.1. K-means một khởi tạo, cùng seed và giới hạn vòng, tol mặc định 1e-4; tiêu chí dừng không giống nhau.
- Thời gian chỉ đo thuật toán ISODATA ở lần tính. Bộ nhớ đệm có tối đa 8 kết quả mỗi hàm; khi lặp lại cấu hình, số thời gian hiển thị là lần tính đã lưu, không phải thời gian bấm nút mới.
- Nhãn “Đã đạt giới hạn vòng lặp” không phải lỗi chương trình: kết quả có thể chưa hội tụ. K là định hướng, không phải số đối tượng được bảo đảm.
- Ảnh tải lên không tự ghi xuống thư mục dự án. Dữ liệu xử lý nằm trong bộ nhớ ứng dụng và cache trong tiến trình.

## Kiểm tra đã thực hiện

- 4 kiểm thử backend: tải/thu nhỏ/xuất ảnh, file lỗi, nền trong suốt, ảnh xám+XY và ảnh quá ít pixel.
- 5 kiểm thử lõi ISODATA hiện có.
- AppTest: đổi K, đổi ảnh mẫu, kết quả cũ được ẩn và chạy lại thành công.
- Agent API trên server thật: trang kết quả, K-means, hai biểu đồ, công thức, đổi tham số, nút chạy, trạng thái chờ upload; đã tải và đọc được PNG/JSON.
- `ty check` cho `streamlit_app.py` và `demo_backend.py`.
- Chưa kiểm tra trực quan ở trình duyệt hoặc chọn file qua hộp thoại hệ điều hành vì kết nối browser automation của phiên làm việc không khả dụng. Phần giải mã file upload và nút uploader đã được kiểm tra riêng, nhưng cần bạn thử kéo thả một ảnh trên trình duyệt của máy trước buổi báo cáo.
