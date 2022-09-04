import os.path as osp
from math import ceil
from typing import Any, Iterator, Optional, Tuple
import re
import numpy as np
from osgeo import gdal
from .functions import RSINDEXS
from .utils import to_uint8
from .error import *
from ..config import SATELLITES
from ..band import creat_band_list_from_config


class SatelliteReader:
    def __init__(self, sensing: str = "ElectronicMap") -> None:
        """卫星图像加载器

        Args:
            sensing (str, optional): 传感器类型或或自定义配置，默认为"ElectronicMap"
        """
        if osp.exists(sensing) and sensing.split(".")[-1] == "yaml":
            config_file = sensing
        elif sensing in SATELLITES.keys():
            config_file = SATELLITES[sensing]
        else:
            SatelliteNotFindError("Cannt find {} in SATELLITES.".format(sensing))
        self._band_list = creat_band_list_from_config(config_file)
        self._src = None
        self._width = None
        self._height = None
        self._bands = None

    @classmethod
    def support_sensing(cls) -> Tuple[str, ...]:
        """支持的传感器类型

        Returns:
            Tuple[str, ...]: 支持的传感器类型
        """
        return tuple(SATELLITES.keys())

    @classmethod
    def support_index(cls) -> Tuple[str, ...]:
        """支持的波段计算公式

        Returns:
            Tuple[str, ...]: 支持的波段计算公式
        """
        return tuple(RSINDEXS.keys())

    def summay(self) -> None:
        """展示所有波段的属性总览"""
        self._band_list.summay()

    def open(self, img_path: str) -> None:
        """打开一个栅格图像

        Args:
            img_path (str): 图像路径

        Raises:
            OpenFileError: 图像路径不存在
            MismatchError: 图像波段数与传感器波段数不一致
        """
        self._src = gdal.Open(img_path)
        if self._src is None:
            raise OpenFileError("Open file failed.")
        self._width = self._src.RasterXSize
        self._height = self._src.RasterYSize
        self._bands = self._src.RasterCount
        if self._bands != len(self._band_list):
            raise MismatchError(
                "The lenght of data and source bands should be equal, but {} is not equal to {}.".format(
                    self._bands, len(self._band_list)
                )
            )

    def get_band(
        self,
        value: Any,
        type: str = "description",
        window: Optional[Tuple[int, int, int, int]] = None,
    ) -> np.ndarray:
        """获取一个波段的值，若索引出的波段大于两个，也只将返回第一个波段的值

        Args:
            value (Any): 查找的值
            type (str, optional): 查找的属性，默认为"description"
            window (Optional[Tuple[int, int, int, int]], optional): 窗口位置，默认为None

        Raises:
            OpenFileError: 图像未打开

        Returns:
            np.ndarray: 该波段的值
        """
        if self._src is None:
            raise OpenFileError("Please read image file first!")
        order = self._band_list.find(value, type)[0].get("order")
        if window is None:
            return self._src.GetRasterBand(order).ReadAsArray()
        else:
            return self._src.GetRasterBand(order).ReadAsArray(
                xoff=window[0], yoff=window[1], win_xsize=window[2], win_ysize=window[3]
            )

    def get_RGB(
        self, to_u8: bool = True, window: Optional[Tuple[int, int, int, int]] = None
    ) -> np.ndarray:
        """获取栅格的真彩色图像

        Args:
            to_u8 (bool, optional): 是否转为UINT8，默认为True.
            window (Optional[Tuple[int, int, int, int]], optional): 窗口位置，默认为None

        Returns:
            np.ndarray: 该栅格的真彩色图像
        """
        ima = np.stack(
            [
                self.get_band("Red", window=window),
                self.get_band("Green", window=window),
                self.get_band("Blue", window=window),
            ],
            axis=-1,
        )
        if to_u8:
            ima = to_uint8(ima)
        return ima

    def sample_band_compute(
        self,
        mode: str = "NDVI",
        eps: float = 2.2204e-16,
        window: Optional[Tuple[int, int, int, int]] = None,
    ) -> np.ndarray:
        """简单的波段计算

        Args:
            mode (str, optional): 需要计算的指数，默认为"NDVI"
            eps (float, optional): 避免分母为零，默认为2.2204e-16.
            window (Optional[Tuple[int, int, int, int]], optional): 窗口位置，默认为None

        Raises:
            FunctionNotFindError: 图像未打开

        Returns:
            np.ndarray: 波段计算的结果
        """
        if mode not in RSINDEXS.keys():
            raise FunctionNotFindError("Cannt find {} in functions.".format(mode))
        func = RSINDEXS[mode]
        values = re.split("\+|-|\*|/", func)
        for value in list(set(values)):
            value = value.strip().replace("(", "").replace(")", "")
            try:
                _ = float(value)
            except:
                exec(value + " = self.get_band(value, window=window) + eps")
        return eval(func)

    def _get_window(
        self, start_loc: Tuple[int, int], block_size: Tuple[int, int]
    ) -> Tuple[int, int, int, int]:
        if len(start_loc) != 2 or len(block_size) != 2:
            raise ValueError("The length start_loc/block_size must be 2.")
        if self._width is None or self._height is None:
            raise OpenFileError("Please read image file first!")
        xoff, yoff = start_loc
        xsize, ysize = block_size
        if (xoff < 0 or xoff > self._width) or (yoff < 0 or yoff > self._height):
            raise ValueError(
                "start_loc must be within [0-{0}, 0-{1}].".format(
                    str(self._width), str(self._height)
                )
            )
        if xoff + xsize > self._width:
            xsize = self._width - xoff
        if yoff + ysize > self._height:
            ysize = self._height - yoff
        return (int(xoff), int(yoff), int(xsize), int(ysize))

    def get_iter(
        self, block_size: Tuple[int, int] = (512, 512), mode: str = "ALL"
    ) -> Iterator[np.ndarray]:
        """迭代返回固定大小的图像块

        Args:
            block_size (Tuple[int, int], optional): 图像块大小，默认为(512, 512)
            mode (str, optional): 图像模式，默认为"ALL"

        Raises:
            OpenFileError: 图像未打开

        Yields:
            Iterator[np.ndarray]: 图像块的迭代器
        """
        if self._width is None or self._height is None:
            raise OpenFileError("Please read image file first!")
        rows = ceil(self._height / block_size[0])
        cols = ceil(self._width / block_size[1])
        for r in range(rows):
            for c in range(cols):
                loc_start = (int(c * block_size[1]), int(r * block_size[0]))
                xoff, yoff, xsize, ysize = self._get_window(loc_start, block_size)
                if mode == "RGB":
                    ima = self.getRGB(window=(xoff, yoff, xsize, ysize))
                elif mode in RSINDEXS.keys():
                    ima = self.sample_band_compute(
                        mode, window=(xoff, yoff, xsize, ysize)
                    )
                else:
                    if self._src is None:
                        raise OpenFileError("Please read image file first!")
                    ima = self._src.ReadAsArray(
                        xoff=xoff, yoff=yoff, xsize=xsize, ysize=ysize
                    )
                h, w = ima.shape[:2] if len(ima.shape) == 3 else ima.shape
                c = ima.shape[-1] if len(ima.shape) == 3 else 1
                if c != 1:
                    tmp = np.zeros((block_size[0], block_size[1], c), dtype=ima.dtype)
                    tmp[:h, :w, :] = ima
                else:
                    tmp = np.zeros((block_size[0], block_size[1]), dtype=ima.dtype)
                    tmp[:h, :w] = ima
                yield tmp
