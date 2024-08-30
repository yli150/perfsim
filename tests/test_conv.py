import unittest
from perfsim.numeric.conv import Conv2D
from perfsim.numeric.conv_block import Conv2DBlock
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

        assert np.allclose(y, yt.numpy(), atol=0.1)

    def test_conv_numerical_block(self):
        # x = np.ones(shape=(1, 3, 12, 12), dtype=np.float16)
        # w = np.ones(shape=(12, 3, 2, 2), dtype=np.float16)
        x = np.random.random(size=(1, 3, 12, 12)).astype(np.float16)
        w = np.random.random(size=(12, 3, 3, 3)).astype(np.float16)
        y = Conv2D(kernel=[3, 3], pads=[0, 0, 0, 0], strides=[2, 2]).inference(x, w)

        yt = Conv2DBlock(kernel=[3, 3], pads=[0, 0, 0, 0], strides=[2, 2]).inference(x, w)

        assert np.allclose(y, yt, atol=0.01)

    def test_conv_numerical_block_x2(self):
        # x = np.ones(shape=(1, 3, 12, 12), dtype=np.float16)
        # w = np.ones(shape=(12, 3, 2, 2), dtype=np.float16)
        x = np.random.random(size=(1, 3, 12, 12)).astype(np.float16)
        w = np.random.random(size=(12, 3, 3, 3)).astype(np.float16)
        y = Conv2D(kernel=[3, 3], pads=[0, 0, 0, 0], strides=[1, 1]).inference(x, w)

        yt = Conv2DBlock(kernel=[3, 3], pads=[0, 0, 0, 0], strides=[1, 1]).inference(x, w)

        assert np.allclose(y, yt, atol=0.01)

    def test_conv_numerical_stencil(self):
        np.random.seed(2)
        x = np.random.random(size=(1, 200, 2, 2)).astype(np.float16)
        w = np.random.random(size=(16, 200, 1, 1)).astype(np.float32)
        y = Conv2D(kernel=[1, 1], pads=[0, 0, 0, 0], strides=[1, 1]).inference(x, w)

        yt = Conv2DBlock(kernel=[1, 1], pads=[0, 0, 0, 0], strides=[1, 1]).inference(x, w)

        assert np.allclose(y, yt, rtol=0.1)

    def test_conv_numerical_stencil_f5(self):
        np.random.seed(2)
        x = np.random.random(size=(1, 200, 8, 8)).astype(np.float16)
        w = np.random.random(size=(16, 200, 3, 3)).astype(np.float32)
        y = Conv2D(kernel=[3, 3], pads=[0, 0, 0, 0], strides=[1, 1]).inference(x, w)

        yt = Conv2DBlock(kernel=[3, 3], pads=[0, 0, 0, 0], strides=[1, 1]).inference(x, w)

        assert np.allclose(y, yt, rtol=0.1)