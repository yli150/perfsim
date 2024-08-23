import numpy as np
from typing import List
import math
from numpy.lib.stride_tricks import sliding_window_view, as_strided


def array_offset(x):
    """Get offset of array data from base data in bytes.
    """
    if x.base is None:
        return 0

    base_start = x.base.__array_interface__['data'][0]
    start = x.__array_interface__['data'][0]
    return start - base_start


class Conv2D():
    def __init__(self, kernel: List[int], pads: List[int], strides: List[int]):
        self.kernel = kernel
        self.pads = pads
        self.strides = strides

    def inference(self, activation: np.ndarray, weights: np.ndarray):
        """
        Do sliding_window inference to transform activation [N, C, H, W] to [N, C, H, W, K , K]

        Args:
            activation: [N, C, H, W]
            weights: [M, C, H, W]

        Returns:

        """
        #  Activation from [N, C, H, W] to [N, C, H, W, Kh , Kw]
        windows = self.sliding_window(activation)
        # Transpose to [N, H, W, Kh, Kw, C]
        windows_ = np.transpose(windows, (0, 2, 3, 4, 5, 1))
        # Weight to [OC, Kh, Kw, C]
        wgt_ = np.transpose(weights, (0, 2, 3, 1))

        out = np.einsum('nhwijc, kijc -> nhwk', windows_, wgt_)

        out = np.transpose(out, (0, 3, 1, 2))
        return out

    def sliding_window(self, activation: np.ndarray):
        '''
        Activation [N, C, H, W] 
        Windows    [N, C, H, W, K , K]
        '''

        # padding on spatial.
        bottom, left, top, right = self.pads

        act = np.pad(activation, pad_width=((0, 0), (0, 0), (bottom, top), (left, right)), mode='constant')

        nb, nc, nh, nw = act.shape
        kh, kw = self.kernel
        sh, sw = self.strides
        # oh, ow
        oh = math.floor((nh - kh) / sh + 1)
        ow = math.floor((nw - kw) / sw + 1)

        n_stride, c_stride, h_stride, w_stride = act.strides

        y_strides = (n_stride, c_stride, sh * h_stride, sw * w_stride, h_stride, w_stride)

        # our impl
        # y = np.ndarray((nb, nc, oh, ow, kh, kw),
        #                dtype=act.dtype,
        #                buffer=act.data,
        #                offset=array_offset(act),
        #                strides=y_strides)

        y = as_strided(act, (nb, nc, oh, ow, kh, kw), y_strides)

        return y
