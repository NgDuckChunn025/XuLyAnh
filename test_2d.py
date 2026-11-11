"""
test_2d.py - Kiểm thử ISODATA trên dữ liệu 2D giả lập TRƯỚC khi áp dụng cho ảnh.

Gồm 4 phép thử:
  Test 1: Tắt tách/gộp -> ISODATA phải cho kết quả tương đương K-means (kiểm tra tính đúng đắn).
  Test 2: Khởi tạo THỪA tâm (10 tâm, thực tế 4 cụm) -> cơ chế GỘP phải giảm số cụm về 4.
  Test 3: Khởi tạo THIẾU tâm (2 tâm, thực tế 4 cụm) -> cơ chế TÁCH phải tăng số cụm lên 4.
  Test 4: Cụm nhỏ/nhiễu -> cơ chế LOẠI phải bỏ các cụm ít mẫu.

Chạy:  python test_2d.py        (hình lưu vào results/test2d/)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from isodata import isodata
from kmeans import kmeans

OUT = "results/test2d"
os.makedirs(OUT, exist_ok=True)


def make_data(seed=0):
    """4 cụm Gauss 2D (mỗi cụm 150 điểm, độ lệch chuẩn ~0.8), cách nhau khoảng 6 đơn vị."""
    rng = np.random.default_rng(seed)
    centers = np.array([[0, 0], [6, 0], [0, 6], [6, 6]], dtype=float)
    X = np.vstack([c + rng.normal(0, 0.8, (150, 2)) for c in centers])
    return X, centers


def plot_process(X, hist, title, fname, max_panels=8):
    """Vẽ scatter từng vòng lặp: màu = cụm, dấu X đỏ = tâm cụm, tiêu đề ghi thao tác của vòng."""
    n = min(len(hist["centers"]), max_panels)
    cols = 4
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3.6 * rows), squeeze=False)
    for i in range(rows * cols):
        ax = axes[i // cols, i % cols]
        if i >= n:
            ax.axis("off")
            continue
        ax.scatter(X[:, 0], X[:, 1], c=hist["labels"][i], cmap="tab20", s=6, alpha=0.6)
        c = hist["centers"][i]
        ax.scatter(c[:, 0], c[:, 1], marker="X", s=120, c="red", edgecolors="k")
        ax.set_title(f"Vòng {i+1}: Nc={hist['n_clusters'][i]} | {hist['events'][i]}", fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle(title, fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, fname), dpi=110)
    plt.close(fig)


def main():
    X, true_centers = make_data()
    N = len(X)
    ok_all = True
    # Tham số chung cho dữ liệu này: sigma thật ~0.8 < theta_S=1.2; các cụm cách nhau 6 > theta_c
    common = dict(K=4, theta_N=10, theta_S=1.2, theta_c=2.5, L=3, max_iter=20, store_labels=True)

    # ---- Test 1: tắt tách/gộp -> phải giống K-means ----
    print("\n=== Test 1: ISODATA (tắt tách/gộp) so với K-means ===")
    l_km, c_km, h_km, _ = kmeans(X, 4, n_init=1)
    l_iso, c_iso, h_iso, _ = isodata(X, K=4, theta_N=1, theta_S=1e9, theta_c=0.0, max_iter=30)
    sse_km, sse_iso = h_km["sse"][-1], h_iso["final_sse"]
    ok = len(c_iso) == 4 and abs(sse_iso - sse_km) / sse_km < 0.01
    ok_all &= ok
    print(f"K-means SSE = {sse_km:.2f} | ISODATA SSE = {sse_iso:.2f} | số cụm = {len(c_iso)} -> {'ĐẠT' if ok else 'KHÔNG ĐẠT'}")

    # ---- Test 2: thừa tâm -> gộp ----
    print("\n=== Test 2: khởi tạo 10 tâm, cần gộp về ~4 ===")
    l, c, h, n_it = isodata(X, init_k=10, verbose=True, **common)
    ok = len(c) == 4 and any("gộp" in e for e in h["events"])
    ok_all &= ok
    print(f"Số cụm cuối = {len(c)} sau {n_it} vòng -> {'ĐẠT' if ok else 'KHÔNG ĐẠT'}")
    plot_process(X, h, "Test 2: khởi tạo thừa 10 tâm -> GỘP về 4 cụm", "test2_merge.png")
    h_merge = h

    # ---- Test 3: thiếu tâm -> tách ----
    print("\n=== Test 3: khởi tạo 2 tâm, cần tách lên ~4 ===")
    l, c, h, n_it = isodata(X, init_k=2, verbose=True, **common)
    ok = len(c) == 4 and any("tách" in e for e in h["events"])
    ok_all &= ok
    print(f"Số cụm cuối = {len(c)} sau {n_it} vòng -> {'ĐẠT' if ok else 'KHÔNG ĐẠT'}")
    plot_process(X, h, "Test 3: khởi tạo thiếu 2 tâm -> TÁCH lên 4 cụm", "test3_split.png")
    h_split = h

    # ---- Test 4: thêm nhiễu thưa -> cụm nhỏ bị loại ----
    print("\n=== Test 4: thêm 6 điểm nhiễu xa, cụm nhỏ phải bị loại ===")
    rng = np.random.default_rng(1)
    Xn = np.vstack([X, rng.uniform(-6, 12, (6, 2)) * np.array([1.0, 1.0])])
    l, c, h, n_it = isodata(Xn, init_k=12, verbose=True, **{**common, "theta_N": 15})
    ok = len(c) == 4 and any("loại" in e for e in h["events"])
    ok_all &= ok
    print(f"Số cụm cuối = {len(c)} -> {'ĐẠT' if ok else 'KHÔNG ĐẠT'}")
    plot_process(Xn, h, "Test 4: có nhiễu, cụm < theta_N mẫu bị LOẠI", "test4_discard.png")

    # ---- Đồ thị số cụm theo vòng lặp ----
    plt.figure(figsize=(6, 4))
    plt.plot(range(1, len(h_merge["n_clusters"]) + 1), h_merge["n_clusters"], "o-", label="khởi tạo 10 tâm (gộp)")
    plt.plot(range(1, len(h_split["n_clusters"]) + 1), h_split["n_clusters"], "s-", label="khởi tạo 2 tâm (tách)")
    plt.axhline(4, color="gray", ls="--", label="số cụm thật = 4")
    plt.xlabel("Vòng lặp"); plt.ylabel("Số cụm"); plt.title("Số cụm theo vòng lặp")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(OUT, "n_clusters_curve.png"), dpi=120)
    plt.close()

    print("\n" + ("TẤT CẢ ĐẠT" if ok_all else "CÓ TEST KHÔNG ĐẠT - xem log phía trên"))
    print(f"Hình đã lưu trong {OUT}/")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
