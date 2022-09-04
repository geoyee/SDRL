import numpy as np
from skimage import exposure


def to_uint8(im, is_linear=True):
    """将栅格转为UINT8

    Args:
        im (np.ndarray): 栅格图像
        is_linear (bool, optional): 是否使用2%线性拉伸，默认为True

    Returns:
        np.ndarray: UINT8的栅格图像
    """

    # 2% linear stretch
    def _two_percent_linear(image, max_out=255, min_out=0):
        def _gray_process(gray, maxout=max_out, minout=min_out):
            # Get the corresponding gray level at 98% in the histogram.
            high_value = np.percentile(gray, 98)
            low_value = np.percentile(gray, 2)
            truncated_gray = np.clip(gray, a_min=low_value, a_max=high_value)
            processed_gray = (
                (truncated_gray - low_value) / (high_value - low_value)
            ) * (maxout - minout)
            return np.uint8(processed_gray)

        if len(image.shape) == 3:
            processes = []
            for b in range(image.shape[-1]):
                processes.append(_gray_process(image[:, :, b]))
            result = np.stack(processes, axis=2)
        else:  # if len(image.shape) == 2
            result = _gray_process(image)
        return np.uint8(result)

    # Simple image standardization
    def _sample_norm(image):
        stretches = []
        if len(image.shape) == 3:
            for b in range(image.shape[-1]):
                stretched = exposure.equalize_hist(image[:, :, b])
                stretched /= float(np.max(stretched))
                stretches.append(stretched)
            stretched_img = np.stack(stretches, axis=2)
        else:  # if len(image.shape) == 2
            stretched_img = exposure.equalize_hist(image)
        return np.uint8(stretched_img * 255)

    dtype = im.dtype.name
    if dtype != "uint8":
        im = _sample_norm(im)
    if is_linear:
        im = _two_percent_linear(im)
    return im
