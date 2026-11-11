"""
run_isodata.py - Chạy ISODATA trên ảnh và so sánh với K-means.

Ví dụ:
    python run_isodata.py images/phongcanh.jpg
    python run_isodata.py images/phongcanh.jpg -k 6 --init-k 12 --theta-s 25 --theta-c 30 --space lab
    python run_isodata.py images/phongcanh.jpg --verbose

Gợi ý tham số (ảnh 8-bit, mỗi kênh 0..255):
    theta_N : ~0.2% số pixel (mặc định tự tính)
    theta_S : 15..40  (nhỏ -> tách nhiều, ra nhiều cụm)
    theta_c : 20..50  (lớn -> gộp nhiều, ra ít cụm)
Đầu ra: results/isodata/<tên>_<tham số>.png  (gốc | K-means | ISODATA | số cụm theo vòng)
"""
import argparse
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from isodata import isodata
from kmeans import kmeans
from utils import (load_image, save_image, make_synthetic_image,
                   image_to_features, features_to_image)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", default=None, help="đường dẫn ảnh (bỏ trống = ảnh giả)")
    ap.add_argument("-k", type=int, default=5, help="số cụm mong muốn K")
    ap.add_argument("--init-k", type=int, default=None, help="số tâm khởi tạo (mặc định = K)")
    ap.add_argument("--theta-n", type=int, default=None, help="số pixel tối thiểu/cụm (mặc định 0.2%% N)")
    ap.add_argument("--theta-s", type=float, default=25.0)
    ap.add_argument("--theta-c", type=float, default=30.0)
    ap.add_argument("-L", type=int, default=2, help="số cặp gộp tối đa mỗi vòng")
    ap.add_argument("-I", type=int, default=30, help="số vòng lặp tối đa")
    ap.add_argument("--space", default="rgb", choices=["rgb", "lab", "gray"])
    ap.add_argument("--xy", action="store_true")
    ap.add_argument("--size", type=int, default=200)
    ap.add_argument("--tol", type=float, default=0.1,
                    help="ngưỡng dịch chuyển tâm để coi là hội tụ (đơn vị màu; ảnh nên dùng ~0.1)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    rgb = load_image(args.image, args.size) if args.image else make_synthetic_image()
    h, w = rgb.shape[:2]
    X = image_to_features(rgb, args.space, use_xy=args.xy)
    N = len(X)
    theta_n = args.theta_n if args.theta_n is not None else max(10, int(0.002 * N))
    print(f"Ảnh {w}x{h} (N={N}) | không gian màu = {args.space} | xy = {args.xy}")
    print(f"Tham số: K={args.k}, init_k={args.init_k or args.k}, theta_N={theta_n}, "
          f"theta_S={args.theta_s}, theta_c={args.theta_c}, L={args.L}, I={args.I}")

    # --- ISODATA ---
    t = time.time()
    labels_i, centers_i, hist, n_it = isodata(
        X, K=args.k, theta_N=theta_n, theta_S=args.theta_s, theta_c=args.theta_c,
        L=args.L, max_iter=args.I, init_k=args.init_k, tol=args.tol,
        seed=args.seed, verbose=args.verbose)
    t_iso = time.time() - t
    k_final = len(centers_i)
    sse_iso = hist["final_sse"]
    seg_iso = features_to_image(labels_i, centers_i, (h, w), args.space)

    # --- K-means với K cố định (= K người dùng chọn) ---
    t = time.time()
    labels_k, centers_k, hk, _ = kmeans(X, args.k, n_init=1, max_iter=args.I, seed=args.seed)
    t_km = time.time() - t
    seg_km = features_to_image(labels_k, centers_k, (h, w), args.space)

    # --- K-means với K = số cụm ISODATA tìm được (so sánh công bằng cùng số cụm) ---
    labels_f, centers_f, hf, _ = kmeans(X, k_final, n_init=1, max_iter=args.I, seed=args.seed)
    seg_f = features_to_image(labels_f, centers_f, (h, w), args.space)

    print(f"\nISODATA : {k_final} cụm | SSE = {sse_iso:,.0f} | {n_it} vòng "
          f"({'hội tụ' if hist['converged'] else 'hết số vòng'}) | {t_iso:.2f}s")
    print(f"K-means : {args.k} cụm | SSE = {hk['sse'][-1]:,.0f} | {t_km:.2f}s")
    print(f"K-means : {k_final} cụm (bằng số cụm ISODATA) | SSE = {hf['sse'][-1]:,.0f}")

    # --- Lưu kết quả ---
    out = "results/isodata"
    os.makedirs(out, exist_ok=True)
    name = os.path.splitext(os.path.basename(args.image))[0] if args.image else "synthetic"
    tag = (f"{name}_{args.space}{'_xy' if args.xy else ''}_k{args.k}"
           f"_s{args.theta_s:g}_c{args.theta_c:g}_n{theta_n}_init{args.init_k or args.k}"
           f"_L{args.L}_I{args.I}_tol{args.tol:g}_size{args.size}_seed{args.seed}")
    save_image(f"{out}/{tag}_isodata.png", seg_iso)

    fig, ax = plt.subplots(1, 5, figsize=(21, 4))
    ax[0].imshow(rgb);     ax[0].set_title("Ảnh gốc")
    ax[1].imshow(seg_km);  ax[1].set_title(f"K-means (K={args.k})")
    ax[2].imshow(seg_iso); ax[2].set_title(f"ISODATA ({k_final} cụm)")
    ax[3].imshow(seg_f); ax[3].set_title(f"K-means cùng K={k_final}")
    for a in ax[:4]:
        a.axis("off")
    its = range(1, len(hist["n_clusters"]) + 1)
    ax[4].plot(its, hist["n_clusters"], "o-")
    ax[4].axhline(args.k, color="gray", ls="--", label=f"K mong muốn = {args.k}")
    ax[4].set_xlabel("Vòng lặp"); ax[4].set_ylabel("Số cụm")
    ax[4].set_title("Số cụm theo vòng lặp"); ax[4].legend(); ax[4].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{out}/{tag}_compare.png", dpi=110)
    plt.close(fig)
    print(f"\nĐã lưu: {out}/{tag}_compare.png")


if __name__ == "__main__":
    main()
