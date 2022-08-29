import yaml
import pandas as pd
from typing import Union, Optional, Iterable, List, Any
from .error import NotFindError


class Band:
    __slots__ = "_attrs"

    def __init__(
        self,
        tag: str,
        order: int,
        resolution: Union[int, float],
        wavelength: Optional[Union[float, Iterable[float]]] = None,
        description: Optional[str] = None,
    ) -> None:
        self._attrs = {
            "tag": tag,  # 该波段的标签
            "order": order,  # 该波段的索引偏移
            "resolution": resolution,  # 该波段图像的分辨率
            "wavelength": wavelength,  # 该波段的波长
            "description": description,  # 该波段的相关描述
        }

    def get(self, type: str = "description") -> Any:
        if type not in self._attrs.keys():
            raise NotFindError("Cannt find {} in band attrs.".format(type))
        return self._attrs[type]

    def set(self, value: Any, type: str = "description") -> None:
        if type not in self._attrs.keys():
            raise NotFindError("Cannt find {} in band attrs.".format(type))
        self._attrs[type] = value

    def summay(self) -> None:
        print(pd.DataFrame(data=[self._attrs]))


class BandList:
    def __init__(self, bands: Iterable[Band]) -> None:
        self.band_list = tuple(bands)

    def __len__(self) -> int:
        return len(self.band_list)

    def find(self, index: Any, type: str = "description") -> List[Band]:
        if self.__len__ == 0 or type not in self.band_list[0]._attrs:
            raise NotFindError("Cannt find {} in band list.".format(type))
        result = []
        for band in self.band_list:
            if index == band.get(type):
                result.append(band)
        return result

    def summay(self) -> None:
        dfs = []
        for band in self.band_list:
            dfs.append(band._attrs)
        print(pd.DataFrame(data=dfs))


def creat_band_list_from_config(yaml_path: str) -> BandList:
    band_list = []
    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.load(f.read(), Loader=yaml.Loader)
        for ib in cfg["bands"]:
            b = cfg["bands"][ib]
            band_list.append(
                Band(
                    b["tag"],
                    b["order"],
                    b["resolution"],
                    b["wavelength"],
                    b["description"],
                )
            )
    return BandList(band_list)
