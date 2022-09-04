from typing import Union, Optional, Iterable, List, Any
import yaml
import pandas as pd
from .error import AttrNotFindError


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
        """波段类

        Args:
            tag (str): 该波段的标签
            order (int): 该波段的索引偏移
            resolution (Union[int, float]): 该波段图像的分辨率
            wavelength (Optional[Union[float, Iterable[float]]], optional): 该波段的波长，默认为None
            description (Optional[str], optional): 该波段的相关描述，默认为None
        """
        self._attrs = {
            "tag": tag,
            "order": order,
            "resolution": resolution,
            "wavelength": wavelength,
            "description": description,
        }

    def get(self, type: str = "description") -> Any:
        """获取波段的某个属性

        Args:
            type (str, optional): 需要获取的属性，默认为"description"

        Raises:
            AttrNotFindError: 该属性不存在

        Returns:
            Any: 属性值
        """
        if type not in self._attrs.keys():
            raise AttrNotFindError("Cannt find {} in band attrs.".format(type))
        return self._attrs[type]

    def set(self, value: Any, type: str = "description") -> None:
        """设置波段的某个属性

        Args:
            value (Any): 属性值
            type (str, optional): 需要设置的属性，默认为"description"

        Raises:
            AttrNotFindError: 该属性不存在
        """
        if type not in self._attrs.keys():
            raise AttrNotFindError("Cannt find {} in band attrs.".format(type))
        self._attrs[type] = value

    def summay(self) -> None:
        """展示波段的属性"""
        print(pd.DataFrame(data=[self._attrs]))


class BandList:
    def __init__(self, bands: Iterable[Band]) -> None:
        """波段列表类

        Args:
            bands (Iterable[Band]): 一个包含多个波段的序列
        """
        self.band_list = tuple(bands)

    def __len__(self) -> int:
        return len(self.band_list)

    def find(self, value: Any, type: str = "description") -> List[Band]:
        """从某种属性中查找满足条件的波段

        Args:
            value (Any): 查找的值
            type (str, optional): 查找的属性，默认为"description"

        Raises:
            AttrNotFindError: 该属性不存在或波段列表中没有波段

        Returns:
            List[Band]: 满足条件的波段组成的列表
        """
        if self.__len__ == 0 or type not in self.band_list[0]._attrs:
            raise AttrNotFindError("Cannt find {} in band list.".format(type))
        result = []
        for band in self.band_list:
            if type != "wavelength":
                if value == band.get(type):
                    result.append(band)
            else:
                wl = band.get(type)
                if isinstance(wl, (int, float)):
                    if value == wl:
                        result.append(band)
                else:
                    if value >= wl[0] and value <= wl[1]:
                        result.append(band)
        return result

    def summay(self) -> None:
        """展示所有波段的属性总览"""
        dfs = []
        for band in self.band_list:
            dfs.append(band._attrs)
        print(pd.DataFrame(data=dfs))


def creat_band_list_from_config(yaml_path: str) -> BandList:
    """通过配置文件创建波段列表

    Args:
        yaml_path (str): 配置文件的路径

    Returns:
        BandList: 波段列表
    """
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
