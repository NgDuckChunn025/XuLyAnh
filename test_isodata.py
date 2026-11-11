"""Kiểm thử hồi quy: python -m unittest test_isodata -v."""
import unittest
import numpy as np
from isodata import isodata


class IsodataTests(unittest.TestCase):
    def setUp(self):
        self.X = np.random.default_rng(4).normal(size=(100, 2))
        self.params = dict(K=3, theta_N=1, theta_S=25, theta_c=0)

    def test_final_sse_matches_returned_partition(self):
        labels, centers, hist, it = isodata(self.X, max_iter=1, **self.params)
        self.assertAlmostEqual(hist['final_sse'], ((self.X-centers[labels])**2).sum())
        np.testing.assert_array_equal(labels, ((self.X[:, None]-centers)**2).sum(2).argmin(1))
        self.assertEqual(it, 1)
        self.assertFalse(hist['converged'])

    def test_invalid_parameters(self):
        for extra in [dict(max_iter=0), dict(K=0), dict(init_k=0), dict(init_k=101),
                      dict(theta_N=-1), dict(theta_S=np.nan), dict(theta_c=-1),
                      dict(L=-1), dict(split_k=0), dict(tol=-1), dict(init='unknown')]:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                isodata(self.X, **{**self.params, **extra})

    def test_invalid_data(self):
        for X in [[], [1, 2], np.empty((0, 2)), [[np.nan, 0]], [[np.inf, 0]]]:
            with self.subTest(X=X), self.assertRaises(ValueError):
                isodata(X, **self.params)

    def test_constant_image(self):
        labels, centers, hist, _ = isodata(np.ones((20, 3)), **self.params)
        self.assertEqual(len(centers), 1)
        self.assertEqual(hist['final_sse'], 0)
        self.assertTrue(hist['converged'])
        self.assertTrue((labels == 0).all())

    def test_final_skipped_merge_is_not_convergence(self):
        X = np.array([[0.], [0.], [10.], [10.]])
        _, _, hist, _ = isodata(X, K=2, theta_N=1, theta_S=100, theta_c=20, max_iter=2)
        self.assertFalse(hist['converged'])


if __name__ == '__main__':
    unittest.main()
