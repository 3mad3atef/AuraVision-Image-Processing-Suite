import cv2
import numpy as np


def get_info(image):
    h, w = image.shape[:2]
    return h, w


def to_gray(image):
    if len(image.shape) == 2:
        return image.copy()
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def extract_channel(image, channel):
    if len(image.shape) == 2:
        return image.copy()

    if channel == "blue":
        return image[:, :, 0].copy()
    elif channel == "green":
        return image[:, :, 1].copy()
    elif channel == "red":
        return image[:, :, 2].copy()


def roi_range(image, y1, y2, x1, x2):
    h, w = image.shape[:2]
    y1 = max(0, min(y1, h - 1))
    y2 = max(y1 + 1, min(y2, h))
    x1 = max(0, min(x1, w - 1))
    x2 = max(x1 + 1, min(x2, w))
    return image[y1:y2, x1:x2].copy()


def histogram_image(image):
    gray = to_gray(image)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)
    ax.plot(hist)
    ax.set_title("Histogram")
    ax.set_xlim([0, 256])
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    buf = np.asarray(canvas.buffer_rgba())
    return cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR)


def gamma_correction(image, gamma=2.0):
    inv = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)


def min_max_stretch(image):
    img = image.astype(np.float32)
    mn, mx = img.min(), img.max()
    if mx == mn:
        return image.copy()
    out = (img - mn) * 255.0 / (mx - mn)
    return out.astype(np.uint8)


def average_filter(image):
    kernel = np.ones((3, 3), np.float32) / 9.0
    return cv2.filter2D(image, -1, kernel)


def laplacian_filter(image):
    gray = to_gray(image)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return cv2.convertScaleAbs(lap)


def remove_salt_pepper(image):
    return cv2.medianBlur(image, 3)


def outlier_method(image, threshold=30):
    img_float = image.astype(np.float32)
    mean = cv2.blur(img_float, (3, 3))
    diff = np.abs(img_float - mean)
    result = img_float.copy()
    result[diff > threshold] = mean[diff > threshold]
    return result.astype(np.uint8)


def sobel_filter(image):
    gray = to_gray(image)

    kernel_x = np.array([
        [-1, -2, -1],
        [ 0,  0,  0],
        [ 1,  2,  1]
    ], dtype=np.float32)

    kernel_y = kernel_x.T

    gx = cv2.filter2D(gray, cv2.CV_64F, kernel_x)
    gy = cv2.filter2D(gray, cv2.CV_64F, kernel_y)

    magnitude = np.sqrt(gx**2 + gy**2)
    return cv2.convertScaleAbs(magnitude)


def prewitt_filter(image):
    gray = to_gray(image)

    kernel_x = np.array([
        [-1, -1, -1],
        [ 0,  0,  0],
        [ 1,  1,  1]
    ], dtype=np.float32)

    kernel_y = kernel_x.T

    gx = cv2.filter2D(gray, cv2.CV_64F, kernel_x)
    gy = cv2.filter2D(gray, cv2.CV_64F, kernel_y)

    magnitude = np.sqrt(gx**2 + gy**2)
    return cv2.convertScaleAbs(magnitude)


def _morph(image, op):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(image, op, kernel)


def dilation(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


def erosion(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


def opening(image):
    return _morph(image, cv2.MORPH_OPEN)


def closing(image):
    return _morph(image, cv2.MORPH_CLOSE)