"""
kmeans.py - K-means tự cài đặt bằng NumPy (dùng làm baseline so sánh với ISODATA).

Thuật toán (Lloyd):
    1. Khởi tạo K tâm.
    2. Gán mỗi điểm vào tâm gần nhất.
    3. Cập nhật tâm = trung bình các điểm trong cụm.
    4. Lặp lại 2-3 đến khi tâm gần như không đổi (hội tụ) hoặc hết max_iter.
"""
import numpy as np


def pairwise_sq_dist(X, C):
    """Bình phương khoảng cách Euclid giữa mọi điểm X (N,d) và mọi tâm C (K,d) -> (N,K).

    Dùng khai triển ||x-c||^2 = ||x||^2 - 2 x.c + ||c||^2 để tránh tạo mảng (N,K,d) rất tốn RAM.
    """
    d2 = (X ** 2).sum(1)[:, None] - 2 * X @ C.T + (C ** 2).sum(1)[None, :]
    return np.maximum(d2, 0)  # chặn sai số làm tròn âm


def init_centers(X, k, method="kmeans++", rng=None):
    rng = rng or np.random.default_rng()
    n = len(X)
    if method == "random":
        return X[rng.choice(n, k, replace=False)].copy()

    # k-means++: chọn tâm đầu ngẫu nhiên, các tâm sau chọn với xác suất ~ khoảng cách^2 tới tâm gần nhất
    centers = [X[rng.integers(n)]]
    for _ in range(1, k):
        d2 = pairwise_sq_dist(X, np.array(centers)).min(axis=1)
        probs = d2 / d2.sum() if d2.sum() > 0 else None
        centers.append(X[rng.choice(n, p=probs)])
    return np.array(centers)


def _kmeans_once(X, k, max_iter, tol, init, rng):
    centers = init_centers(X, k, init, rng)
    sse_hist = []

    for it in range(1, max_iter + 1):
        # Bước 2: gán nhãn
        d2 = pairwise_sq_dist(X, centers)
        labels = d2.argmin(axis=1)
        sse_hist.append(d2[np.arange(len(X)), labels].sum())

        # Bước 3: cập nhật tâm
        new_centers = centers.copy()
        for j in range(k):
            members = X[labels == j]
            if len(members) > 0:
                new_centers[j] = members.mean(axis=0)
            else:  # cụm rỗng: bốc lại 1 điểm ngẫu nhiên
                new_centers[j] = X[rng.integers(len(X))]

        shift = np.linalg.norm(new_centers - centers)
        centers = new_centers
        if shift < tol:
            break

    # gán nhãn lần cuối theo tâm cuối cùng và tính SSE cuối
    d2 = pairwise_sq_dist(X, centers)
    labels = d2.argmin(axis=1)
    final_sse = d2[np.arange(len(X)), labels].sum()
    sse_hist.append(final_sse)
    return labels, centers, sse_hist, it


def kmeans(X, k, max_iter=100, tol=1e-4, init="kmeans++", n_init=5, seed=0):
    """K-means chạy n_init lần với khởi tạo khác nhau, giữ lần có SSE nhỏ nhất.

    (K-means chỉ hội tụ về cực tiểu CỤC BỘ nên kết quả phụ thuộc khởi tạo;
     chạy nhiều lần là cách khắc phục chuẩn.)

    Trả về: labels (N,), centers (K,d), history (dict: sse theo vòng), n_iter.
    """
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(n_init):
        res = _kmeans_once(X, k, max_iter, tol, init, rng)
        if best is None or res[2][-1] < best[2][-1]:
            best = res
    labels, centers, sse_hist, it = best
    return labels, centers, {"sse": sse_hist}, it
