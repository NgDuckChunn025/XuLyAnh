"""
baseline_kmeans.py - Pipeline cơ bản: đọc ảnh -> K-means -> dựng lại ảnh -> so sánh.

Chạy:
    python baseline_kmeans.py                         # dùng ảnh giả
    python baseline_kmeans.py images/anh1.jpg -k 5    # dùng ảnh thật
    python baseline_kmeans.py images/anh1.jpg -k 5 --space lab --xy
"""
import argparse
import os
import time

import matplotlib
matplotlib.use("Agg")  # lưu file, không bật cửa sổ; đổi thành "TkAgg" nếu muốn xem trực tiếp
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

from kmeans import kmeans
from utils import (load_image, save_image, make_synthetic_image,
                   image_to_features, features_to_image)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", default=None, help="đường dẫn ảnh (bỏ trống = ảnh giả)")
    ap.add_argument("-k", type=int, default=4)
    ap.add_argument("--space", default="rgb", choices=["rgb", "lab", "gray"])
    ap.add_argument("--xy", action="store_true", help="thêm tọa độ (x,y) vào đặc trưng")
    ap.add_argument("--size", type=int, default=200, help="cạnh dài tối đa sau khi thu nhỏ")
    args = ap.parse_args()

    rgb = load_image(args.image, args.size) if args.image else make_synthetic_image()
    h, w = rgb.shape[:2]
    X = image_to_features(rgb, args.space, use_xy=args.xy)
    print(f"Ảnh {w}x{h}, X.shape = {X.shape}, không gian màu = {args.space}, xy = {args.xy}")

    # --- K-means tự viết ---
    t = time.time()
    labels, centers, hist, n_iter = kmeans(X, args.k, n_init=5)
    t_own = time.time() - t
    sse_own = hist["sse"][-1]
    seg_own = features_to_image(labels, centers, (h, w), args.space)

    # --- K-means của sklearn (đối chiếu) ---
    t = time.time()
    sk = KMeans(n_clusters=args.k, n_init=1, random_state=0).fit(X)
    t_sk = time.time() - t
    seg_sk = features_to_image(sk.labels_, sk.cluster_centers_, (h, w), args.space)

    print(f"Tự viết : SSE = {sse_own:,.0f} | {n_iter} vòng | {t_own:.2f}s")
    print(f"sklearn : SSE = {sk.inertia_:,.0f} | {sk.n_iter_} vòng | {t_sk:.2f}s")

    # --- Lưu kết quả ---
    os.makedirs("results", exist_ok=True)
    name = os.path.splitext(os.path.basename(args.image))[0] if args.image else "synthetic"
    tag = f"{name}_k{args.k}_{args.space}{'_xy' if args.xy else ''}"
    save_image(f"results/{tag}_kmeans.png", seg_own)

    fig, ax = plt.subplots(1, 4, figsize=(16, 4))
    ax[0].imshow(rgb);     ax[0].set_title("Ảnh gốc")
    ax[1].imshow(seg_own); ax[1].set_title(f"K-means tự viết (K={args.k})")
    ax[2].imshow(seg_sk);  ax[2].set_title("K-means sklearn")
    ax[3].plot(hist["sse"], marker="o"); ax[3].set_title("SSE theo vòng lặp")
    ax[3].set_xlabel("vòng"); ax[3].set_ylabel("SSE")
    for a in ax[:3]:
        a.axis("off")
    plt.tight_layout()
    plt.savefig(f"results/{tag}_compare.png", dpi=120)
    print(f"Đã lưu: results/{tag}_compare.png")


if __name__ == "__main__":
    main()
