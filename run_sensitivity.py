"""Khảo sát từng tham số trên một ảnh, 3 seed; xuất JSON, Markdown và PNG.

python run_sensitivity.py
python run_sensitivity.py --image images/logo.jpg --space rgb --seeds 0 1 2 3 4
"""
import argparse
import hashlib
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
from isodata import isodata
from utils import load_image, image_to_features


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', default='images/phongcanh.jpg')
    ap.add_argument('--space', choices=['rgb', 'lab', 'gray'], default='lab')
    ap.add_argument('--size', type=int, default=200)
    ap.add_argument('--seeds', nargs='+', type=int, default=[0, 1, 2])
    ap.add_argument('--out', default='results/sensitivity')
    args = ap.parse_args()
    if args.size < 1 or len(args.seeds) != len(set(args.seeds)):
        ap.error('size phải >= 1; các seed không được trùng nhau')
    X = image_to_features(load_image(args.image, args.size), args.space)
    base = dict(K=5, init_k=10, theta_N=max(10, int(.002*len(X))),
                theta_S=25., theta_c=30., L=2, max_iter=50, tol=.1)
    configs = [('baseline', {}) , ('S=15', dict(theta_S=15.)), ('S=40', dict(theta_S=40.)),
               ('c=20', dict(theta_c=20.)), ('c=50', dict(theta_c=50.)),
               ('init=2', dict(init_k=2)), ('init=5', dict(init_k=5))]
    out = Path(args.out)/datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    out.mkdir(parents=True)
    rows, summaries = [], []
    for name, change in configs:
        group = []
        for seed in args.seeds:
            params = {**base, **change, 'seed': seed}
            start = time.perf_counter()
            labels, centers, hist, it = isodata(X, **params)
            elapsed = time.perf_counter()-start
            # Kiểm tra số liệu cuối trước khi đưa vào báo cáo.
            np.testing.assert_allclose(hist['final_sse'], ((X-centers[labels])**2).sum())
            row = dict(config=name, parameters=params, k_final=len(centers),
                       occupied_clusters=len(np.unique(labels)), sse=hist['final_sse'],
                       iterations=it, converged=hist['converged'], time_s=elapsed,
                       events=hist['events'], n_clusters=hist['n_clusters'])
            rows.append(row); group.append(row)
        counts = [r['k_final'] for r in group]
        errors = [r['sse'] for r in group]
        summaries.append(dict(config=name, k_values=counts, k_mean=float(np.mean(counts)),
                              sse_mean=float(np.mean(errors)),
                              sse_std_sample=float(np.std(errors, ddof=1)) if len(errors)>1 else None,
                              converged=sum(r['converged'] for r in group)))
        print(f'{name}: K={counts}, hội tụ {summaries[-1]["converged"]}/{len(group)}', flush=True)
    metadata = dict(image=args.image, image_sha256=hashlib.sha256(Path(args.image).read_bytes()).hexdigest(),
                    space=args.space, size=args.size, pixels=len(X), seeds=args.seeds, base=base,
                    python=platform.python_version(), numpy=np.__version__, opencv=cv2.__version__,
                    matplotlib=matplotlib.__version__)
    (out/'experiment.json').write_text(json.dumps(dict(metadata=metadata, summaries=summaries, runs=rows),
                                                 ensure_ascii=False, indent=2), encoding='utf-8')
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for i, summary in enumerate(summaries):
        group = [r for r in rows if r['config']==summary['config']]
        offsets = np.linspace(-.15, .15, len(group)) if len(group)>1 else [0]
        for offset, row in zip(offsets, group):
            color = '#147d64' if row['converged'] else '#cc5a24'
            axes[0].scatter(i+offset, row['k_final'], color=color, s=40)
            axes[1].scatter(i+offset, row['sse']/1e6, color=color, s=40)
    for ax in axes:
        ax.set_xticks(range(len(configs)), [name for name, _ in configs], rotation=25)
        ax.grid(axis='y', alpha=.25)
    axes[0].set(ylabel='Số cụm cuối', title='Mỗi điểm là một seed')
    axes[1].set(ylabel='SSE (triệu)', title='SSE khác K không dùng để xếp hạng chất lượng')
    fig.suptitle(f'{Path(args.image).name} / {args.space.upper()} — xanh: hội tụ; cam: hết 50 vòng')
    fig.tight_layout()
    fig.savefig(out/'sensitivity.png', dpi=140)
    plt.close(fig)
    lines = ['# Khảo sát độ nhạy tham số', '',
             f'Ảnh `{args.image}`, {args.space.upper()}, {len(X)} pixel, seeds={args.seeds}.',
             f'Cấu hình cơ sở: `{base}`. Mỗi hàng chỉ thay tham số ghi trong tên cấu hình.',
             'K liệt kê theo thứ tự seed. SD là độ lệch chuẩn mẫu của SSE (ddof=1), không phải độ lệch chuẩn pixel dùng để tách.',
             'Tổng hợp cả lần chưa hội tụ. Không dùng SSE để xếp hạng các hàng khác K; chưa khảo sát tương tác tham số hoặc toàn bộ bộ ảnh.', '',
             '| Cấu hình | K cuối theo seed | SSE trung bình | SD SSE | Hội tụ |',
             '|---|---|---:|---:|---:|']
    for s in summaries:
        sd = 'N/A' if s['sse_std_sample'] is None else f"{s['sse_std_sample']:.0f}"
        lines.append(f"| {s['config']} | {s['k_values']} | {s['sse_mean']:.0f} | {sd} | {s['converged']}/{len(args.seeds)} |")
    lines += ['', '![Khảo sát tham số](sensitivity.png)', '',
              'Đọc cùng `experiment.json` để xem cấu hình và sự kiện từng vòng. Đây là khảo sát mô tả, không phải tìm bộ tham số tối ưu.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(f'Đã lưu: {out.resolve()}')


if __name__ == '__main__':
    main()
