"""Thực nghiệm tiến độ: 5 ảnh x RGB/Lab, một seed, cùng ngân sách khởi tạo.

python run_batch_isodata.py --out results/progress
Mỗi lần chạy lưu thư mục con riêng để tránh ghi đè thực nghiệm trước.
"""
import argparse
import csv
import json
import platform
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sklearn
from sklearn.metrics import silhouette_score
from isodata import isodata
from kmeans import kmeans
from utils import load_image, image_to_features, features_to_image


def silhouette(X, labels, seed):
    # Dùng cùng tập pixel lấy mẫu cho các phương pháp trong một cấu hình.
    indices = np.random.default_rng(seed).choice(len(X), min(2000, len(X)), replace=False)
    y = labels[indices]
    if not 1 < len(np.unique(y)) < len(y):
        return None
    return float(silhouette_score(X[indices], y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--images', default='images')
    ap.add_argument('--out', default='results/progress')
    ap.add_argument('--size', type=int, default=200)
    ap.add_argument('-k', type=int, default=5)
    ap.add_argument('--init-k', type=int, default=10)
    ap.add_argument('--theta-s', type=float, default=25)
    ap.add_argument('--theta-c', type=float, default=30)
    ap.add_argument('--max-iter', type=int, default=50)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()
    if args.size < 1:
        ap.error('--size phải >= 1')
    paths = sorted(p for p in Path(args.images).iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'))
    if not paths:
        ap.error('Không tìm thấy ảnh đầu vào')
    out = Path(args.out) / datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    out.mkdir(parents=True)
    metadata = dict(arguments=vars(args), python=platform.python_version(), numpy=np.__version__,
                    opencv=cv2.__version__, sklearn=sklearn.__version__,
                    protocol='One initialization per algorithm; K-means tol=1e-4, ISODATA tol=0.1; same iteration cap; timings exclude metrics and rendering.')
    (out/'config.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    rows = []
    for path in paths:
        rgb = load_image(str(path), args.size)
        for space in ('rgb', 'lab'):
            X = image_to_features(rgb, space)
            theta_n = max(10, int(.002*len(X)))
            start = time.perf_counter()
            li, ci, hi, ni = isodata(X, K=args.k, init_k=args.init_k, theta_N=theta_n,
                                    theta_S=args.theta_s, theta_c=args.theta_c, L=2,
                                    max_iter=args.max_iter, tol=.1, seed=args.seed)
            ti = time.perf_counter()-start
            results = [('ISODATA', li, ci, hi['final_sse'], ni, ti, hi['converged'])]
            for method, k in [('KMeans_fixed', args.k), ('KMeans_matched', len(ci))]:
                start = time.perf_counter()
                labels, centers, hist, iterations = kmeans(X, k, n_init=1, max_iter=args.max_iter, seed=args.seed)
                elapsed = time.perf_counter()-start
                results.append((method, labels, centers, float(hist['sse'][-1]), iterations, elapsed, None))
            fig, axes = plt.subplots(1, 5, figsize=(20, 4))
            axes[0].imshow(rgb); axes[0].set_title('Ảnh gốc')
            for ax, result in zip(axes[1:4], results):
                method, labels, centers, sse, iterations, elapsed, converged = result
                sil = silhouette(X, labels, args.seed)
                rows.append(dict(image=path.name, space=space, pixels=len(X), method=method,
                                 K_target=args.k, init_k=args.init_k if method=='ISODATA' else len(centers),
                                 k_final=len(centers), occupied_clusters=len(np.unique(labels)),
                                 theta_N=theta_n, theta_S=args.theta_s, theta_c=args.theta_c,
                                 seed=args.seed, sse=sse, silhouette=sil, iterations=iterations,
                                 converged=converged, time_s=elapsed))
                ax.imshow(features_to_image(labels, centers, rgb.shape[:2], space))
                ax.set_title(f'{method}\nK={len(centers)}, SSE={sse:.2e}', fontsize=10)
            for ax in axes[:4]:
                ax.axis('off')
            axes[4].plot(range(1, ni+1), hi['n_clusters'], 'o-', markersize=3)
            axes[4].axhline(args.k, linestyle='--', color='gray')
            axes[4].set(xlabel='Vòng lặp', ylabel='Số cụm', title='Hội tụ' if hi['converged'] else 'Hết số vòng')
            fig.suptitle(f'{path.name} — {space.upper()} — seed={args.seed}')
            fig.tight_layout()
            fig.savefig(out/f'{path.stem}_{space}_compare.png', dpi=120)
            plt.close(fig)
            trace = {k: hi[k] for k in ('n_clusters', 'sse', 'shift', 'events', 'converged', 'final_sse')}
            (out/f'{path.stem}_{space}_history.json').write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'{path.name} {space}: K={len(ci)}, iterations={ni}, converged={hi["converged"]}', flush=True)
    with (out/'summary.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    lines = ['# Kết quả thực nghiệm tiến độ', '',
             'Một seed, chưa phải kết luận tổng quát. SSE chỉ so sánh trong cùng ảnh và không gian đặc trưng.',
             'K-means matched dùng số tâm cuối của ISODATA. Cả hai chạy một khởi tạo và cùng giới hạn vòng; tiêu chí dừng khác nhau.',
             'Silhouette lấy tối đa 2.000 pixel. Thời gian không gồm tính chỉ số và vẽ hình.', '',
             '| Ảnh | Màu | K cuối | Vòng | Hội tụ | SSE ISO | SSE KM cùng K | Sil ISO |',
             '|---|---|---:|---:|---|---:|---:|---:|']
    for i in range(0, len(rows), 3):
        r, matched = rows[i], rows[i+2]
        sil = 'N/A' if r['silhouette'] is None else f"{r['silhouette']:.3f}"
        lines.append(f"| {r['image']} | {r['space']} | {r['k_final']} | {r['iterations']} | {r['converged']} | {r['sse']:.0f} | {matched['sse']:.0f} | {sil} |")
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(f'Đã lưu: {out.resolve()}')


if __name__ == '__main__':
    main()
