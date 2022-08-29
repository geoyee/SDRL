import numpy as np
from osgeo import gdal
from typing import Any
from .functions import RSINDEXS
from .error import *
from ..config import SATELLITES
from ..band import creat_band_list_from_config


class SatelliteDataloader:
    __slots__ = "_src", "_band_list"

    def __init__(self, sensing: str) -> None:
        if sensing not in SATELLITES.keys():
            SatelliteNotFindError("Cannt find {} in satellites.".format(sensing))
        self._band_list = creat_band_list_from_config(SATELLITES[sensing])
        self._src = None

    def summay(self) -> None:
        self._band_list.summay()

    def read(self, img_path: str) -> None:
        self._src = gdal.Open(img_path)

    def get_band(self, index: Any, type: str = "description") -> np.ndarray:
        if self._src is None:
            raise FileNotOpenError("Please read image file first!")
        order = self._band_list.find(index, type)[0].get("order")
        return self._src.GetRasterBand(order).ReadAsArray()

    def getRGB(self) -> np.ndarray:
        return np.stack(
            [
                self.get_band("Red"),
                self.get_band("Green"),
                self.get_band("Blue"),
            ],
            axis=-1,
        )

    def sample_band_compute(self, mode: str = "NDVI") -> np.ndarray:
        eps = 1e-12
        R = self.get_band("Red") + eps
        G = self.get_band("Green") + eps
        B = self.get_band("Blue") + eps
        NIR = self.get_band("NIR") + eps
        if mode not in RSINDEXS.keys():
            raise FunctionNotFindError("Cannt find {} in functions.".format(mode))
        return eval(RSINDEXS[mode])
