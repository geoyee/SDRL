from sdrl import SatelliteDataloader, to_uint8
import matplotlib.pyplot as plt


if __name__ == "__main__":
    gf1_wfv_reader = SatelliteDataloader(sensing="GF1_WFV")
    gf1_wfv_reader.summay()
    gf1_wfv_reader.read("testdata/GF1_WFV2_E109.5_N32.6_20200425_L1A0004761605.tiff")
    rgb = gf1_wfv_reader.getRGB()
    plt.imshow(to_uint8(rgb, is_linear=True))
    plt.show()
    ndvi = gf1_wfv_reader.sample_band_compute("NDVI")
    plt.imshow(ndvi)
    plt.show()
