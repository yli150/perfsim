import numpy as np
from typing import List
import math
from numpy.lib.stride_tricks import sliding_window_view, as_strided
from .stencil import Stencil


class Conv2DBlock():
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

        out = self.stencil_partition(windows_, wgt_)

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

        y = np.zeros(shape=(nb, nc, oh, ow, kh, kw), dtype=act.dtype)

        for _oh in range(oh):
            for _ow in range(ow):
                m = act[:, :, _oh * sh:_oh * sh + kh, _ow * sw:_ow * sw + kw]
                y[:, :, _oh, _ow] = m

        return y

    def stencil_partition(self, act: np.ndarray, weight: np.ndarray):
        '''
        Act [N, H, W, Kh, Kw, C]
        Weight [K, Kh, kw, C]
        '''

        # <H, W, IC, OC>
        stencil = Stencil(16, 8, 16, 128)

        n, h, w, kh, kw, c = act.shape

        oc = weight.shape[0]

        # reshape to [N, H, W, Kh*Kw*C]
        act = np.reshape(act, (n, h, w, -1))
        weight = np.reshape(weight, (oc, -1))

        out = np.zeros(shape=(n, h, w, oc)).astype(np.float32)
        for _k in range(0, oc, stencil.K):
            for _y in range(0, h, stencil.H):
                for _x in range(0, w, stencil.W):
                    for _c in range(0, c * kh * kw, stencil.C):
                        _a = act[:, _y:_y + stencil.H, _x:_x + stencil.W, _c:_c + stencil.C]
                        _wgt = weight[_k:_k + stencil.K, _c:_c + stencil.C]
                        _psum = np.einsum('nhwc, kc -> nhwk', _a, _wgt)
                        out[:, _y:_y + stencil.H, _x:_x + stencil.W, _k:_k + stencil.K] += _psum
        return out.astype(np.float32)

    def dispatch_to_pe(self, act: np.ndarray, wgt: np.ndarray):
        # <H, W, IC, OC>
        pe_array = Stencil(16, 8, 16, 128)
        cube = Stencil(4, 4, 16, 16)

        pe_pairs = {
            # id, act offset, wgt offset
            # OC 0->16
            0: ((0, 0, 0, 0), (0, 0)),
            1: ((0, 4, 0, 0), (0, 0)),
            2: ((4, 0, 0, 0), (0, 0)),
            3: ((4, 4, 0, 0), (0, 0)),
            4: ((8, 0, 0, 0), (0, 0)),
            5: ((8, 4, 0, 0), (0, 0)),
            6: ((12, 0, 0, 0), (0, 0)),
            7: ((12, 4, 0, 0), (0, 0)),
            # OC 16->32
            8: ((0, 0, 0, 0), (32, 0)),
            9: ((0, 4, 0, 0), (32, 0)),
            10: ((4, 0, 0, 0), (32, 0)),
            11: ((4, 4, 0, 0), (32, 0)),
            12: ((8, 0, 0, 0), (32, 0)),
            13: ((8, 4, 0, 0), (32, 0)),
            14: ((12, 0, 0, 0), (32, 0)),
            15: ((12, 4, 0, 0), (32, 0)),
        }
