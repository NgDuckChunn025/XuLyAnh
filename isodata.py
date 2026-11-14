"""
isodata.py - Thuật toán ISODATA tự cài đặt bằng NumPy.

ISODATA = K-means + 3 cơ chế tự điều chỉnh số cụm:
    (1) LOẠI cụm quá nhỏ        (ít hơn theta_N mẫu)
    (2) TÁCH cụm quá phân tán   (độ lệch chuẩn lớn hơn theta_S)
    (3) GỘP hai cụm quá gần     (khoảng cách tâm nhỏ hơn theta_c)

Tham số:
    K        : số cụm MONG MUỐN (chỉ là "số định hướng", số cụm thật có thể khác)
    theta_N  : số mẫu tối thiểu của một cụm
    theta_S  : ngưỡng độ lệch chuẩn để tách cụm
    theta_c  : ngưỡng khoảng cách giữa hai tâm để gộp cụm
    L        : số cặp cụm tối đa được gộp trong MỘT vòng lặp
    max_iter : số vòng lặp tối đa (I)
    init_k   : số tâm khởi tạo ban đầu (mặc định = K)
    split_k  : hệ số 0 < k <= 1, tâm mới khi tách = tâm cũ ± split_k * sigma_max

Sơ đồ biến thể đang cài đặt (nguồn đối chiếu và khác biệt: docs/HIEU_ISODATA_VA_VAN_DAP.md):
    1. assign          : gán mỗi điểm vào tâm gần nhất
    2. discard_small   : loại cụm < theta_N mẫu, gán lại các điểm của nó
    3. update_centers  : tâm = trung bình cụm
    4. Chọn thao tác:
         - vòng cuối                     -> dừng, không tách/gộp nữa
         - số cụm Nc <= K/2              -> TÁCH
         - vòng chẵn hoặc Nc >= 2K       -> GỘP
         - còn lại (vòng lẻ)             -> TÁCH
    5. Dừng khi 2 vòng liên tiếp không có loại/tách/gộp và tâm gần như không dịch
       chuyển, hoặc đủ max_iter vòng.
"""
import numpy as np
from kmeans import pairwise_sq_dist, init_centers


# --------------------------------------------------------------------------
# Các khối cơ bản
# --------------------------------------------------------------------------
def assign(X, centers):
    """Gán mỗi điểm vào tâm gần nhất. Trả về labels (N,) và bình phương khoảng cách nhỏ nhất (N,)."""
    d2 = pairwise_sq_dist(X, centers)
    labels = d2.argmin(axis=1)
    return labels, d2[np.arange(len(X)), labels]


def discard_small(X, centers, labels, theta_N):
    """Loại các cụm có ít hơn theta_N mẫu rồi gán lại toàn bộ điểm.

    Điểm của cụm bị loại sẽ chuyển sang tâm gần nhất trong các tâm còn lại.
    Không bao giờ loại hết: nếu mọi cụm đều nhỏ thì giữ lại cụm lớn nhất.
    Trả về (centers mới, labels mới, số cụm bị loại).
    """
    counts = np.bincount(labels, minlength=len(centers))
    keep = counts >= max(theta_N, 1)          # cụm rỗng luôn bị loại
    if not keep.any():
        keep[counts.argmax()] = True
    n_discarded = int((~keep).sum())
    if n_discarded:
        centers = centers[keep]
        labels, _ = assign(X, centers)
    return centers, labels, n_discarded


def update_centers(X, labels, centers):
    """Tâm mới = trung bình các điểm trong cụm (vectorize bằng bincount). Trả về (centers, counts)."""
    k = len(centers)
    counts = np.bincount(labels, minlength=k)
    new = centers.copy()
    nz = counts > 0
    for j in range(X.shape[1]):
        sums = np.bincount(labels, weights=X[:, j], minlength=k)
        new[nz, j] = sums[nz] / counts[nz]
    return new, counts


def cluster_stats(X, labels, centers):
    """Thống kê từng cụm phục vụ quyết định tách:
        counts : số mẫu n_j
        sigma  : độ lệch chuẩn theo từng chiều (k, d)
        d_j    : khoảng cách trung bình từ điểm tới tâm của cụm j
        d_avg  : khoảng cách trung bình toàn cục (trung bình có trọng số theo n_j)
    """
    k = len(centers)
    counts = np.bincount(labels, minlength=k).astype(float)
    counts_safe = np.maximum(counts, 1)
    sigma = np.zeros_like(centers, dtype=float)
    for j in range(X.shape[1]):
        s1 = np.bincount(labels, weights=X[:, j], minlength=k)
        s2 = np.bincount(labels, weights=X[:, j] ** 2, minlength=k)
        mean = s1 / counts_safe
        sigma[:, j] = np.sqrt(np.maximum(s2 / counts_safe - mean ** 2, 0.0))
    dist = np.linalg.norm(X - centers[labels], axis=1)
    d_j = np.bincount(labels, weights=dist, minlength=k) / counts_safe
    d_avg = (counts * d_j).sum() / counts.sum()
    return counts, sigma, d_j, d_avg


# --------------------------------------------------------------------------
# Tách và gộp
# --------------------------------------------------------------------------
def split_clusters(centers, counts, sigma, d_j, d_avg, K, theta_N, theta_S, split_k=0.5):
    """Tách cụm j thành 2 tâm (mu ± gamma) dọc theo chiều có độ lệch chuẩn lớn nhất, nếu:
        (a) sigma_max > theta_S, VÀ
        (b) [d_j > d_avg VÀ n_j > 2(theta_N+1)]  HOẶC  Nc <= K/2
    Điều kiện (b) tránh tách cụm vốn đã chặt, hoặc cụm quá ít mẫu (tách ra sẽ bị loại ngay).
    Trả về (centers mới, số cụm đã tách).
    """
    nc = len(centers)
    out, n_split = [], 0
    for j in range(nc):
        dim = sigma[j].argmax()
        s_max = sigma[j, dim]
        cond_a = s_max > theta_S
        cond_b = (d_j[j] > d_avg and counts[j] > 2 * (theta_N + 1)) or (nc <= K / 2)
        if cond_a and cond_b and counts[j] >= 2:
            gamma = split_k * s_max
            c1, c2 = centers[j].copy(), centers[j].copy()
            c1[dim] += gamma
            c2[dim] -= gamma
            out += [c1, c2]
            n_split += 1
        else:
            out.append(centers[j])
    return np.array(out), n_split


def merge_clusters(centers, counts, theta_c, L):
    """Gộp tối đa L cặp tâm có khoảng cách < theta_c, ưu tiên cặp gần nhất.
    Mỗi cụm chỉ được gộp tối đa 1 lần trong một vòng.
    Tâm mới = trung bình có trọng số theo số mẫu: (n_i*mu_i + n_j*mu_j)/(n_i+n_j).
    Trả về (centers mới, số cặp đã gộp).
    """
    nc = len(centers)
    if nc < 2:
        return centers, 0
    d = np.sqrt(pairwise_sq_dist(centers, centers))
    iu, ju = np.triu_indices(nc, k=1)
    dist = d[iu, ju]
    used, merged, n_merge = set(), [], 0
    for idx in np.argsort(dist):
        if n_merge >= L or dist[idx] >= theta_c:
            break
        i, j = int(iu[idx]), int(ju[idx])
        if i in used or j in used:
            continue
        merged.append((counts[i] * centers[i] + counts[j] * centers[j]) / (counts[i] + counts[j]))
        used |= {i, j}
        n_merge += 1
    kept = [centers[j] for j in range(nc) if j not in used]
    return np.array(kept + merged), n_merge


# --------------------------------------------------------------------------
# Vòng lặp chính
# --------------------------------------------------------------------------
def isodata(X, K, theta_N, theta_S, theta_c, L=1, max_iter=30, init_k=None,
            split_k=0.5, tol=1e-3, init="kmeans++", seed=0,
            store_labels=False, verbose=False):
    """Chạy ISODATA. Trả về: labels (N,), centers (Kc,d), history (dict), n_iter.

    history gồm (mỗi phần tử ứng với một vòng lặp):
        n_clusters : số cụm tại vòng đó (sau khi loại, trước khi tách/gộp)
        sse        : tổng bình phương sai số
        shift      : độ dịch chuyển lớn nhất của các tâm
        events     : mô tả thao tác, vd "tách 2", "gộp 1", "loại 1"
        centers    : tâm của vòng đó (để vẽ lại quá trình)
        labels     : nhãn của vòng đó (chỉ khi store_labels=True)
        converged  : True nếu dừng do hội tụ (False nếu hết max_iter)
        final_sse  : SSE tính từ nhãn và tâm thực sự trả về (sau gán nhãn cuối)
    """
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 2 or 0 in X.shape or not np.isfinite(X).all():
        raise ValueError("X phải là ma trận 2D không rỗng, chỉ chứa số hữu hạn")
    for name, value, minimum in (("K", K, 1), ("max_iter", max_iter, 1),
                                  ("theta_N", theta_N, 0), ("L", L, 0)):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < minimum:
            raise ValueError(f"{name} phải là số nguyên >= {minimum}")
    initial_count = K if init_k is None else init_k
    if (isinstance(initial_count, (bool, np.bool_)) or
            not isinstance(initial_count, (int, np.integer)) or
            not 1 <= initial_count <= len(X)):
        raise ValueError("Số tâm khởi tạo phải là số nguyên từ 1 đến số mẫu")
    for name, value in (("theta_S", theta_S), ("theta_c", theta_c), ("tol", tol)):
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"{name} phải hữu hạn và >= 0")
    if not np.isfinite(split_k) or not 0 < split_k <= 1:
        raise ValueError("split_k phải thuộc (0, 1]")
    if init not in ("random", "kmeans++"):
        raise ValueError("init phải là random hoặc kmeans++")
    rng = np.random.default_rng(seed)
    centers = init_centers(X, initial_count, init, rng)
    hist = dict(n_clusters=[], sse=[], shift=[], events=[], centers=[], labels=[], converged=False)
    quiet = 0   # số vòng liên tiếp "yên tĩnh" (không loại/tách/gộp, tâm không dịch)

    for it in range(1, max_iter + 1):
        # 1-3: gán, loại cụm nhỏ, cập nhật tâm
        labels, _ = assign(X, centers)
        centers, labels, n_disc = discard_small(X, centers, labels, theta_N)
        new_centers, counts = update_centers(X, labels, centers)
        shift = np.linalg.norm(new_centers - centers, axis=1).max()
        centers = new_centers
        nc = len(centers)
        sse = float(((X - centers[labels]) ** 2).sum())

        hist["n_clusters"].append(nc)
        hist["sse"].append(sse)
        hist["shift"].append(float(shift))
        hist["centers"].append(centers.copy())
        if store_labels:
            hist["labels"].append(labels.copy())

        # 4: chọn thao tác
        events = []
        if n_disc:
            events.append(f"loại {n_disc}")
        n_split = n_merge = 0
        if it == max_iter:
            events.append("vòng cuối")
        elif nc <= K / 2 or (it % 2 == 1 and nc < 2 * K):
            counts_f, sigma, d_j, d_avg = cluster_stats(X, labels, centers)
            centers, n_split = split_clusters(centers, counts_f, sigma, d_j, d_avg,
                                              K, theta_N, theta_S, split_k)
            if n_split:
                events.append(f"tách {n_split}")
        else:  # vòng chẵn hoặc nc >= 2K
            centers, n_merge = merge_clusters(centers, counts, theta_c, L)
            if n_merge:
                events.append(f"gộp {n_merge}")
        hist["events"].append(", ".join(events) if events else "không đổi")

        if verbose:
            print(f"Vòng {it:2d}: Nc={nc:2d} | SSE={sse:14,.1f} | shift={shift:8.4f} | {hist['events'][-1]}")

        # 5: kiểm tra hội tụ
        # Vòng cuối bỏ qua tách/gộp, nên không dùng nó làm bằng chứng hội tụ.
        quiet = quiet + 1 if (it < max_iter and n_disc == 0 and n_split == 0 and n_merge == 0 and shift <= tol) else 0
        if quiet >= 2:
            hist["converged"] = True
            break

    labels, _ = assign(X, centers)
    hist["final_sse"] = float(((X - centers[labels]) ** 2).sum())
    return labels, centers, hist, it
