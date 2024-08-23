import unittest
from perfsim.numeric.conv import Conv2D
import numpy as np
import torch


class TestConvNumeric(unittest.TestCase):
    def test_conv_numerical(self):
        # x = np.ones(shape=(1, 3, 12, 12), dtype=np.float16)
        # w = np.ones(shape=(12, 3, 2, 2), dtype=np.float16)
        x = np.random.random(size=(1, 3, 12, 12)).astype(np.float16)
        w = np.random.random(size=(12, 3, 2, 2)).astype(np.float16)
        y = Conv2D(kernel=[2, 2], pads=[0, 0, 0, 0], strides=[2, 2]).inference(x, w)

        xt = torch.Tensor(x)
        wt = torch.Tensor(w)
        yt = torch.nn.functional.conv2d(xt, wt, stride=[2, 2], padding=[0, 0])

        assert np.allclose(y, yt.numpy(), atol=0.01)

    def test_conv_numerical_k3(self):
        # x = np.ones(shape=(1, 3, 12, 12), dtype=np.float16)
        # w = np.ones(shape=(12, 3, 2, 2), dtype=np.float16)
        x = np.random.random(size=(1, 3, 12, 12)).astype(np.float16)
        w = np.random.random(size=(12, 3, 3, 3)).astype(np.float16)
        y = Conv2D(kernel=[3, 3], pads=[0, 0, 0, 0], strides=[2, 2]).inference(x, w)

        xt = torch.Tensor(x)
        wt = torch.Tensor(w)
        yt = torch.nn.functional.conv2d(xt, wt, stride=[2, 2], padding=[0, 0])

        assert np.allclose(y, yt.numpy(), atol=0.01)