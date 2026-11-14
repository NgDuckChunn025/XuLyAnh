"""Ví dụ tính tay có kiểm chứng bằng các hàm thật: python demo_formulas.py."""
import numpy as np
from isodata import assign, update_centers, cluster_stats, split_clusters, merge_clusters


def main():
    X = np.array([[0.], [2.], [8.], [10.]])
    labels = np.zeros(4, dtype=int)
    centers, _ = update_centers(X, labels, np.array([[0.]]))
    counts, sigma, d_j, d_avg = cluster_stats(X, labels, centers)
    sse = float(((X-centers[labels])**2).sum())
    np.testing.assert_allclose([centers[0, 0], sigma[0, 0], d_avg, sse],
                               [5, np.sqrt(17), 4, 68])
    np.testing.assert_allclose(sse, (counts[:, None]*sigma**2).sum())
    new, n_split = split_clusters(centers, counts, sigma, d_j, d_avg,
                                 K=4, theta_N=1, theta_S=3, split_k=.5)
    assert n_split == 1
    new_labels, _ = assign(X, new)
    updated, new_counts = update_centers(X, new_labels, new)
    split_sse = float(((X-updated[new_labels])**2).sum())
    np.testing.assert_allclose(np.sort(updated[:, 0]), [1, 9])
    np.testing.assert_allclose(split_sse, 4)
    merged, n_merge = merge_clusters(updated, new_counts, theta_c=9, L=1)
    assert n_merge == 1
    merged_sse = float(((X-merged[0])**2).sum())
    penalty = float(np.prod(new_counts)/new_counts.sum()*((updated[0]-updated[1])**2).sum())
    np.testing.assert_allclose(merged_sse-split_sse, penalty)
    print('Dữ liệu một chiều: 0, 2, 8, 10 (ví dụ giáo khoa, không phải ảnh thật)')
    print(f'1. Tâm = {centers[0,0]:.2f}; D_j = D_avg = {d_avg:.2f}')
    print(f'2. Phương sai = 17; sigma = {sigma[0,0]:.4f}; SSE = {sse:.2f}')
    print('3. K=4, Nc=1 <= K/2; sigma > theta_S=3: đủ điều kiện tách.')
    print(f'4. Tâm đề xuất = 5 ± 0.5*sqrt(17) = {new[:,0].round(4).tolist()}')
    print(f'5. Gán lại, cập nhật: tâm {updated[:,0].tolist()}, SSE={split_sse:.2f}')
    print('6. Minh họa riêng bước gộp: khoảng cách hai tâm = 8 < theta_c=9.')
    print(f'7. Tâm gộp = {merged[0,0]:.2f}; SSE={merged_sse:.2f}; tăng {penalty:.2f}')
    print('ĐÃ KIỂM CHỨNG: SSE=sum(n_j*sigma_j^2); công thức tăng SSE khi gộp.')
    print('Đây là chuỗi gọi các khối để học, không phải log của vòng lặp isodata().')


if __name__ == '__main__':
    main()
