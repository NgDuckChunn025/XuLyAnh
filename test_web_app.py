"""Kiểm tra trạng thái UI bằng Streamlit AppTest, không mở trình duyệt."""
import unittest
from streamlit.testing.v1 import AppTest


class WebAppTests(unittest.TestCase):
    def test_new_parameters_require_run(self):
        app = AppTest.from_file('streamlit_app.py', default_timeout=40).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 4)
        app.slider(key='target_k').set_value(6).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(len(app.info), 1)
        app.button(key='run').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 4)
        app.selectbox(key='sample').select('Logo').run()
        self.assertEqual(len(app.metric), 0)
        app.button(key='run').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 4)


if __name__ == '__main__':
    unittest.main()
