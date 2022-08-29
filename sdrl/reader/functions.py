RSINDEXS = {
    "NDVI": "(NIR - R) / (NIR + R)",  # 归一化植被指数
    "EVI": "2.5 * (NIR - R) / (NIR + 6 * R - 7.5 * B + 1)",  # 增强型植被指数
    "RVI": "NIR / R",  # 比值植被指数
    "GNDVI": "(NIR - G) / (NIR + G)",  # 绿色归一化差值植被指数
    "DVI": "NIR - R",  # 差值植被指数
    "NDWI": "(G - NIR) / (G + NIR)",  # 归一化水体指数
    "GCVI": "(NIR / G) - 1",  # 叶绿素指数
}
