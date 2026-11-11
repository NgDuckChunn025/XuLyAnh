# Kết quả thực nghiệm tiến độ

Một seed, chưa phải kết luận tổng quát. SSE chỉ so sánh trong cùng ảnh và không gian đặc trưng.
K-means matched dùng số tâm cuối của ISODATA. Cả hai chạy một khởi tạo và cùng giới hạn vòng; tiêu chí dừng khác nhau.
Silhouette lấy tối đa 2.000 pixel. Thời gian không gồm tính chỉ số và vẽ hình.

| Ảnh | Màu | K cuối | Vòng | Hội tụ | SSE ISO | SSE KM cùng K | Sil ISO |
|---|---|---:|---:|---|---:|---:|---:|
| chandung.jpg | rgb | 6 | 50 | False | 6093461 | 6093426 | 0.625 |
| chandung.jpg | lab | 4 | 50 | False | 4361669 | 4317415 | 0.609 |
| logo.jpg | rgb | 10 | 16 | True | 8739727 | 8739727 | 0.838 |
| logo.jpg | lab | 10 | 14 | True | 3502406 | 3502397 | 0.839 |
| phongcanh.jpg | rgb | 10 | 28 | True | 20007961 | 20007260 | 0.403 |
| phongcanh.jpg | lab | 7 | 18 | True | 9648158 | 9628031 | 0.428 |
| vetinh.jpg | rgb | 4 | 42 | True | 5626521 | 5624311 | 0.475 |
| vetinh.jpg | lab | 2 | 22 | True | 6314152 | 6308273 | 0.544 |
| xquang.jpg | rgb | 8 | 32 | True | 3004760 | 2989808 | 0.638 |
| xquang.jpg | lab | 4 | 36 | True | 4416170 | 4416170 | 0.686 |
