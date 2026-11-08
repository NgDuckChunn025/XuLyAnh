"""
utils.py - Các hàm tiện ích cho bài tập phân cụm ảnh.

Pipeline chung:
    ảnh (H, W, 3)  --image_to_features-->  X (N, d)  --thuật toán phân cụm-->  labels (N,), centers (K, d)
    labels, centers  --features_to_image-->  ảnh đã phân cụm (H, W, 3)
"""
import os
import cv2
import numpy as np


def load_image(path, max_size=200):
    """Đọc ảnh, trả về mảng RGB uint8 (H, W, 3), thu nhỏ nếu cạnh dài hơn max_size.

    Dùng np.fromfile + imdecode thay cho cv2.imread để không lỗi khi đường dẫn
    có dấu tiếng Việt / ký tự Unicode trên Windows.
    """
    data = np.fromfile(path, dtype=np.uint8)
    bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(f"Không đọc được ảnh: {path}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    h, w = rgb.shape[:2]
    scale = max_size / max(h, w)
    if max_size and scale < 1:
        rgb = cv2.resize(rgb, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return rgb


def save_image(path, rgb):
    """Lưu ảnh RGB (an toàn với đường dẫn Unicode)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    ext = os.path.splitext(path)[1] or ".png"
    ok, buf = cv2.imencode(ext, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if ok:
        buf.tofile(path)


def make_synthetic_image(size=150, seed=0):
    """Tạo ảnh giả có 4 vùng màu + nhiễu, dùng khi chưa có ảnh thật để test pipeline."""
    rng = np.random.default_rng(seed)
    img = np.zeros((size, size, 3), dtype=np.float32)
    h = size // 2
    img[:h, :h] = (200, 40, 40)     # đỏ
    img[:h, h:] = (40, 160, 60)     # xanh lá
    img[h:, :h] = (50, 70, 200)     # xanh dương
    img[h:, h:] = (230, 210, 60)    # vàng
    img += rng.normal(0, 12, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)


def image_to_features(rgb, color_space="rgb", use_xy=False, xy_weight=1.0):
    """Chuyển ảnh thành ma trận đặc trưng X có shape (N, d), N = H*W.

    color_space : 'rgb' | 'lab' | 'gray'
    use_xy      : thêm tọa độ (x, y) vào vector đặc trưng (để cụm liền mảng hơn).
    xy_weight   : hệ số nhân cho tọa độ, sau khi đã chuẩn hóa về thang 0..255
                  (0 = bỏ qua vị trí, 1 = vị trí quan trọng ngang màu).
    """
    h, w = rgb.shape[:2]
    if color_space == "rgb":
        feat = rgb.astype(np.float64)
    elif color_space == "lab":
        # OpenCV Lab 8-bit: L, a, b đều được co về 0..255
        feat = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float64)
    elif color_space == "gray":
        feat = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float64)[..., None]
    else:
        raise ValueError("color_space phải là 'rgb', 'lab' hoặc 'gray'")

    X = feat.reshape(-1, feat.shape[-1])

    if use_xy:
        ys, xs = np.mgrid[0:h, 0:w]
        xy = np.stack([xs.ravel() / max(w - 1, 1), ys.ravel() / max(h - 1, 1)], axis=1)
        X = np.hstack([X, xy * 255.0 * xy_weight])
    return X


def features_to_image(labels, centers, shape, color_space="rgb"):
    """Dựng lại ảnh: mỗi pixel nhận màu của tâm cụm mà nó thuộc về.

    shape: (H, W) của ảnh gốc. Nếu X có thêm cột (x, y) thì bỏ chúng đi.
    """
    h, w = shape
    n_color = {"rgb": 3, "lab": 3, "gray": 1}[color_space]
    colors = np.clip(centers[:, :n_color], 0, 255).astype(np.uint8)
    seg = colors[labels].reshape(h, w, n_color)

    if color_space == "lab":
        seg = cv2.cvtColor(seg, cv2.COLOR_LAB2RGB)
    elif color_space == "gray":
        seg = np.repeat(seg, 3, axis=2)
    return seg
