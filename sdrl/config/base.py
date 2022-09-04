import os.path as osp
from glob import glob


PATH = osp.dirname(osp.abspath(__file__))


def get_file_name(filr_path: str) -> str:
    return filr_path.replace("\\", "/").split("/")[-1].split(".")[0]


SATELLITES = {}
satellite_dir = osp.join(PATH, "satellite")
yamls = glob(osp.join(satellite_dir, "*/*.yaml"))
for yaml_file in yamls:
    name = get_file_name(yaml_file)
    SATELLITES[name] = yaml_file
