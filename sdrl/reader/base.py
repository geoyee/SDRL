import numpy as np
from math import ceil
from osgeo import gdal
from typing import Any, Iterable, Optional, Tuple
from .functions import RSINDEXS
from .utils import to_uint8
from .error import *
from ..config import SATELLITES
from ..band import creat_band_list_from_config


class SatelliteReader:
    def __init__(self, sensing: str = "ElectronicMap") -> None:
        if sensing not in SATELLITES.keys():
            SatelliteNotFindError("Cannt find {} in satellites.".format(sensing))
        self._band_list = creat_band_list_from_config(SATELLITES[sensing])
        self._src = None
        self._width = None
        self._height = None
        self._bands = None

    def summay(self) -> None:
        self._band_list.summay()

    def read(self, img_path: str) -> None:
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
        index: Any,
        type: str = "description",
        window: Optional[Tuple[int, int, int, int]] = None,
    ) -> np.ndarray:
        if self._src is None:
            raise FileNotOpenError("Please read image file first!")
        order = self._band_list.find(index, type)[0].get("order")
        if window is None:
            return self._src.GetRasterBand(order).ReadAsArray()
        else:
            return self._src.GetRasterBand(order).ReadAsArray(
                xoff=window[0], yoff=window[1], win_xsize=window[2], win_ysize=window[3]
            )

    def getRGB(
        self, to_u8: bool = True, window: Optional[Tuple[int, int, int, int]] = None
    ) -> np.ndarray:
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
        eps: float = 1e-12,
        window: Optional[Tuple[int, int, int, int]] = None,
    ) -> np.ndarray:
        R = self.get_band("Red", window=window) + eps
        G = self.get_band("Green", window=window) + eps
        B = self.get_band("Blue", window=window) + eps
        NIR = self.get_band("NIR", window=window) + eps
        if mode not in RSINDEXS.keys():
            raise FunctionNotFindError("Cannt find {} in functions.".format(mode))
        return eval(RSINDEXS[mode])

    def _get_window(
        self, start_loc: Tuple[int, int], block_size: Tuple[int, int]
    ) -> Tuple[int, int, int, int]:
        if len(start_loc) != 2 or len(block_size) != 2:
            raise ValueError("The length start_loc/block_size must be 2.")
        if self._width is None or self._height is None:
            raise FileNotOpenError("Please read image file first!")
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
    ) -> Iterable[np.ndarray]:
        if self._width is None or self._height is None:
            raise FileNotOpenError("Please read image file first!")
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
                        raise FileNotOpenError("Please read image file first!")
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
