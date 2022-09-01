import os.path as osp
from glob import glob


SATELLITES = {}
satellite_dir = "sdrl/config/satellite"
yamls = glob(osp.join(satellite_dir, "*/*.yaml"))
for yaml_file in yamls:
    name = yaml_file.replace("\\", "/").split("/")[-1].split(".")[0]
    SATELLITES[name] = yaml_file
