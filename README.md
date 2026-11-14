# XuLyAnh — Phân cụm ảnh bằng ISODATA

BTL môn Xử lý ảnh và Thị giác máy tính. Cài đặt NumPy, phân cụm pixel bằng màu RGB/Lab/gray và tùy chọn tọa độ XY; so sánh với K-means.

## Demo web — ISODATA Studio

```powershell
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.address=127.0.0.1 --server.port=8501
```

Mở **http://127.0.0.1:8501** để tải ảnh, chỉnh tham số, xem ảnh trước/sau, so sánh K-means, xem quá trình và tải PNG/JSON. Có sẵn 5 ảnh mẫu. Xem [hướng dẫn demo web](docs/DEMO_WEB.md) về thao tác, cấu hình và kịch bản trình bày.

## Chạy trên Windows PowerShell

Chạy từ thư mục gốc dự án. Môi trường `venv` hiện có đủ thư viện; Python toàn hệ thống có thể thiếu scikit-learn.

```powershell
.\venv\Scripts\python.exe -m unittest test_isodata -v
.\venv\Scripts\python.exe test_2d.py
.\venv\Scripts\python.exe run_isodata.py images/phongcanh.jpg --space lab -k 5 --init-k 10 -I 50 --verbose
.\venv\Scripts\python.exe run_batch_isodata.py
```

Trên máy mới: tạo môi trường bằng `python -m venv venv`, rồi cài bằng `.\venv\Scripts\python.exe -m pip install -r requirements.txt`.

## Thành phần

- `isodata.py`: thuật toán, các cơ chế loại/tách/gộp và lịch sử vòng lặp.
- `kmeans.py`: baseline tự viết.
- `utils.py`: đọc, chuyển đặc trưng và dựng lại ảnh.
- `run_isodata.py`: demo một ảnh, hiển thị thêm K-means cùng số cụm cuối.
- `run_batch_isodata.py`: thực nghiệm RGB/Lab trên toàn bộ ảnh, lưu CSV, PNG, lịch sử JSON và cấu hình môi trường vào thư mục con mới.
- `test_isodata.py`: kiểm thử hồi quy SSE, dữ liệu/tham số lỗi, ảnh đồng màu và trạng thái hội tụ.
- `test_2d.py`: bốn tình huống trực quan; trả mã lỗi nếu kiểm tra thất bại.
- [Hướng dẫn báo cáo tiến độ](docs/BAO_CAO_TIEN_DO.md).
- [Hiểu công thức, ánh xạ code và luyện vấn đáp](docs/HIEU_ISODATA_VA_VAN_DAP.md).
- [Phân công nhóm 3 người và lịch chuẩn bị](docs/PHAN_CONG_NHOM_3_NGUOI.md).

## Bổ sung để giải thích và khảo sát thuật toán

```powershell
.\venv\Scripts\python.exe demo_formulas.py
.\venv\Scripts\python.exe run_sensitivity.py
```

`demo_formulas.py` kiểm chứng ví dụ bốn điểm bằng chính các hàm tách/gộp; có kiểm tra liên hệ SSE–phương sai và mức tăng SSE khi gộp. `run_sensitivity.py` mặc định chạy ảnh phong cảnh Lab với 7 cấu hình × 3 seed, thay từng tham số so với cấu hình cơ sở; xuất JSON, bảng Markdown và biểu đồ vào thư mục con mới trong `results/sensitivity/`.

Xem [kết quả khảo sát ngày 14/11](results/sensitivity/20261114_002842_746678/RESULTS.md). Khảo sát này chỉ bao phủ một ảnh, chưa phải tối ưu tham số hoặc kết luận tổng quát trên cả bộ dữ liệu.

## Cách đọc kết quả

`history['sse']` giữ trạng thái trong từng vòng, trước tách/gộp. Dùng `history['final_sse']` để đánh giá nhãn và tâm thực sự trả về. Không thay thế lịch sử bằng SSE cuối vì hai giá trị mô tả hai thời điểm khác nhau.

K là định hướng; `init_k` là số tâm ban đầu. `theta_N` là kích thước cụm tối thiểu, `theta_S` là ngưỡng độ lệch chuẩn để tách, `theta_c` là ngưỡng khoảng cách để gộp, L là số cặp gộp tối đa mỗi vòng. Các ngưỡng phụ thuộc thang đo đặc trưng. Lab đang dùng mã hóa 8-bit của OpenCV.

Batch hiện chạy một khởi tạo/phương pháp, cùng giới hạn 50 vòng nhưng tiêu chí dừng khác nhau (ISODATA: dịch chuyển tâm tối đa <= 0.1 và hai vòng không đổi cấu trúc; K-means: chuẩn dịch chuyển toàn bộ tâm < 1e-4). K-means chưa xuất cờ hội tụ nên cột này để trống. Thời gian chỉ đo thuật toán. Silhouette dùng cùng mẫu tối đa 2.000 pixel trong mỗi cấu hình.

Không so trực tiếp SSE khác không gian đặc trưng hoặc khác số cụm để khẳng định phương pháp tốt hơn. SSE thấp không chứng minh nhận diện đối tượng đúng. Đây là phân cụm pixel, chưa phải phân đoạn ngữ nghĩa. Thực nghiệm một seed là kết quả bước đầu; nguồn ảnh và tài liệu thuật toán cần bổ sung vào báo cáo cuối kỳ.
