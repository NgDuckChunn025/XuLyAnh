import unittest
from io import BytesIO
import numpy as np
from PIL import Image
from demo_backend import decode_image, png_bytes, segment_image


class DemoTests(unittest.TestCase):
    def test_upload_resize_and_export(self):
        rgb = np.zeros((100, 200, 3), dtype=np.uint8)
        rgb[:, 100:] = [220, 150, 40]
        decoded, size = decode_image(png_bytes(rgb), 80)
        self.assertEqual(size, (200, 100))
        self.assertEqual(decoded.shape, (40, 80, 3))
        result = segment_image(decoded, K=2, init_k=2, theta_N=1, theta_S=255, theta_c=0)
        self.assertEqual(result['output'].shape, decoded.shape)
        self.assertEqual(result['counts'].sum(), 3200)
        self.assertIsNotNone(result['km'])
        self.assertEqual(Image.open(BytesIO(png_bytes(result['output']))).size, (80, 40))

    def test_invalid_upload(self):
        with self.assertRaises(ValueError):
            decode_image(b'not an image')

    def test_transparency_on_white(self):
        im = Image.new('RGBA', (5, 5), (0, 0, 0, 0))
        buf = BytesIO(); im.save(buf, format='PNG')
        rgb, _ = decode_image(buf.getvalue())
        self.assertTrue((rgb == 255).all())

    def test_gray_xy_and_tiny_image(self):
        rgb = np.full((20, 20, 3), 100, dtype=np.uint8)
        result = segment_image(rgb, space='gray', use_xy=True, K=2, init_k=2,
                               theta_N=1, max_iter=4, compare=False)
        self.assertEqual(result['output'].shape, rgb.shape)
        self.assertFalse(result['km'])
        with self.assertRaises(ValueError):
            segment_image(rgb[:1, :1])


if __name__ == '__main__':
    unittest.main()
