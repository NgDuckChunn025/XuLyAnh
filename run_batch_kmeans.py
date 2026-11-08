"""
run_batch_kmeans.py - Chạy K-means hàng loạt: nhiều ảnh x nhiều K x (RGB, Lab).

Đầu ra (trong results/batch/):
    <tên ảnh>_grid.png : lưới ảnh (hàng = không gian màu, cột = ảnh gốc + các K)
    summary.csv        : bảng SSE, Silhouette, thời gian, số vòng lặp cho mọi cấu hình

Chạy:
    python run_batch_kmeans.py                    # quét thư mục images/
    python run_batch_kmeans.py --ks 3 5 8 12 --size 160
"""
import argparse
import csv
import glob
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score

from kmeans import kmeans
from utils import (load_image, make_synthetic_image,
                   image_to_features, features_to_image)

SPACES = ["rgb", "lab"]


def collect_images(folder, size):
    paths = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff"):
        paths += glob.glob(os.path.join(folder, ext))
    if not paths:
        print(f"[!] Thư mục '{folder}' chưa có ảnh -> dùng 2 ảnh giả để thử.")
        return [("synthetic_a", make_synthetic_image(150, 0)),
                ("synthetic_b", make_synthetic_image(150, 1))]
    return [(os.path.splitext(os.path.basename(p))[0], load_image(p, size))
            for p in sorted(paths)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", default="images")
    ap.add_argument("--ks", type=int, nargs="+", default=[3, 5, 8])
    ap.add_argument("--size", type=int, default=200)
    ap.add_argument("--out", default="results/batch")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rows = []

    for name, rgb in collect_images(args.images, args.size):
        h, w = rgb.shape[:2]
        fig, axes = plt.subplots(len(SPACES), len(args.ks) + 1,
                                 figsize=(3 * (len(args.ks) + 1), 3 * len(SPACES)))
        for r, space in enumerate(SPACES):
            X = image_to_features(rgb, space)
            axes[r, 0].imshow(rgb)
            axes[r, 0].set_title(f"Gốc ({space.upper()})")
            for c, k in enumerate(args.ks, start=1):
                t = time.time()
                labels, centers, hist, n_iter = kmeans(X, k, n_init=3)
                dt = time.time() - t
                sse = hist["sse"][-1]
                sil = silhouette_score(X, labels, sample_size=2000, random_state=0)
                axes[r, c].imshow(features_to_image(labels, centers, (h, w), space))
                axes[r, c].set_title(f"K={k} | SSE={sse:.2e}\nSil={sil:.2f}", fontsize=9)
                rows.append(dict(image=name, space=space, K=k, sse=round(sse),
                                 silhouette=round(sil, 4), iters=n_iter,
                                 time_s=round(dt, 3)))
                print(f"{name:15s} {space:4s} K={k:<3d} SSE={sse:12.0f} "
                      f"Sil={sil:.3f} iters={n_iter:<3d} {dt:.2f}s")
        for a in axes.ravel():
            a.axis("off")
        plt.tight_layout()
        plt.savefig(os.path.join(args.out, f"{name}_grid.png"), dpi=110)
        plt.close(fig)

    with open(os.path.join(args.out, "summary.csv"), "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=rows[0].keys())
        wr.writeheader()
        wr.writerows(rows)
    print(f"\nĐã lưu lưới ảnh và summary.csv vào '{args.out}/'")


if __name__ == "__main__":
    main()
