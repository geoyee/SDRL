from sdrl.band import creat_band_list_from_config


if __name__ == "__main__":
    bands = creat_band_list_from_config("sdrl/config/GF_CN/GF1_WFV4.yaml")
    bands.summay()
    bands.find("Red", "description")[0].summay()
