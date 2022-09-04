"""公式中的索引来自波段的description，目前仅支持四则运算"""

RSINDEXS = {
    "NDVI": "(NIR - Red) / (NIR + Red)",  # 归一化植被指数
    "EVI": "2.5 * (NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 1)",  # 增强型植被指数
    "RVI": "NIR / Red",  # 比值植被指数
    "GNDVI": "(NIR - Green) / (NIR + Green)",  # 绿色归一化差值植被指数
    "DVI": "NIR - Red",  # 差值植被指数
    "NDWI": "(Green - NIR) / (Green + NIR)",  # 归一化水体指数
    "GCVI": "(NIR / Green) - 1",  # 叶绿素指数
}
