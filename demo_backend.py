"""Xử lý ảnh trong bộ nhớ cho web demo; dùng chung lõi ISODATA của dự án."""
from io import BytesIO
import time
import warnings

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from isodata import isodata
from kmeans import kmeans
from utils import image_to_features, features_to_image

MAX_UPLOAD_BYTES = 12 * 1024 * 1024
MAX_PIXELS = 20_000_000


def decode_image(data, max_size=240):
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ValueError('Chọn một ảnh có dung lượng không quá 12 MB.')
    if not 80 <= max_size <= 400:
        raise ValueError('Cạnh xử lý phải từ 80 đến 400 pixel.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as im:
                if im.width * im.height > MAX_PIXELS:
                    raise ValueError('Ảnh quá lớn. Vui lòng dùng ảnh không quá 20 triệu pixel.')
                original_size = im.size
                im = ImageOps.exif_transpose(im).convert('RGBA')
                background = Image.new('RGBA', im.size, 'white')
                background.alpha_composite(im)
                im = background.convert('RGB')
                im.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                rgb = np.asarray(im).copy()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise ValueError('Không đọc được ảnh. Hãy thử một file PNG, JPG hoặc WEBP hợp lệ.') from exc
    return rgb, original_size


def png_bytes(rgb):
    buffer = BytesIO()
    Image.fromarray(np.asarray(rgb, dtype=np.uint8)).save(buffer, format='PNG')
    return buffer.getvalue()


def segment_image(rgb, *, space='lab', use_xy=False, xy_weight=.25, K=5,
                  init_k=10, theta_N=20, theta_S=25., theta_c=30., L=2,
                  max_iter=50, seed=0, compare=True):
    X = image_to_features(rgb, space, use_xy=use_xy, xy_weight=xy_weight)
    if len(X) < max(K, init_k):
        raise ValueError('Ảnh có quá ít pixel so với số tâm. Hãy chọn ảnh lớn hơn hoặc giảm số tâm.')
    start = time.perf_counter()
    labels, centers, history, iterations = isodata(
        X, K=K, init_k=init_k, theta_N=theta_N, theta_S=theta_S,
        theta_c=theta_c, L=L, max_iter=max_iter, tol=.1, seed=seed)
    elapsed = time.perf_counter()-start
    output = features_to_image(labels, centers, rgb.shape[:2], space)
    palette = features_to_image(np.arange(len(centers)), centers, (1, len(centers)), space)[0]
    counts = np.bincount(labels, minlength=len(centers))
    result = dict(original=rgb, output=output, palette=palette, counts=counts,
                  k=len(centers), occupied=int((counts > 0).sum()), iterations=iterations,
                  elapsed=elapsed, sse=history['final_sse'], converged=history['converged'],
                  history={k: history[k] for k in ('n_clusters', 'sse', 'shift', 'events')},
                  km=None)
    if compare:
        start = time.perf_counter()
        lk, ck, hk, nk = kmeans(X, len(centers), n_init=1, max_iter=max_iter, seed=seed)
        result['km'] = dict(image=features_to_image(lk, ck, rgb.shape[:2], space),
                            sse=float(hk['sse'][-1]), iterations=nk,
                            elapsed=time.perf_counter()-start)
    return result
