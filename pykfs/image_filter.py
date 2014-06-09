from PIL import Image
from colorsys import rgb_to_hsv, hsv_to_rgb
import numpy as np
import math
import logging
import os


LOG = logging.getLogger(__name__)


def _filter_pixel_cached(image_filter, r, g, b, a):
    color = (r, g, b, a)
    if color not in image_filter._filters:
        image_filter._filters[color] = image_filter.filter_pixel(r, g, b, a)
    return image_filter._filters[color]


_filter_pixels = np.vectorize(_filter_pixel_cached, excluded=["image_filter"])


class ImageFilter(object):

    def __init__(self, img):
        self.image = img.mode == "RGBA" and img or img.convert("RGBA")
        self._filters = {}

    def _pixel_count(self):
        return self.image.size[0] * self.image.size[1]
    pixel_count = property(_pixel_count)

    def get_filtered(self):
        self.analyze()
        self.draw()
        return self.filter_image

    filter_pixel_cached = _filter_pixel_cached

    def filter_pixels(self, r, g, b, a):
        return np.array(_filter_pixels(self, r, g, b, a))

    def filter_pixel(self, r, g, b, a):
        raise NotImplementedError()

    def analyze(self):
        pass

    def draw(self):
        arr = np.asarray(self.image).astype("float")
        arr = np.rollaxis(arr, -1)
        result = self.filter_pixels(*arr)
        result = np.rollaxis(result, 0, len(result.shape)).astype("uint8")
        self.filter_image = Image.fromarray(result, "RGBA")


DEFAULT_LIGHT_RATIO = 0.15


def darkflash(img, light_ratio=DEFAULT_LIGHT_RATIO):
    LOG.info('Creating darkflash for {0}...'.format(os.path.basename(img.filename)))
    d = DarkFlash(img, light_ratio=light_ratio)
    new_img = d.get_filtered()
    LOG.info('Finished creating darkflash for {0}...'.format(os.path.basename(img.filename)))
    return new_img


class DarkFlash(ImageFilter):

    def __init__(self, *args, **kwargs):
        self.light_ratio = kwargs.pop("light_ratio", DEFAULT_LIGHT_RATIO)
        super(DarkFlash, self).__init__(*args, **kwargs)

    def isvisible(self, color):
        return color[3] > 10

    def analyze(self):
        self.colors = [x for x in self.image.getcolors(self.pixel_count) if self.isvisible(x[1])]
        self.colors.sort(key=lambda x: sum(x[1][:-1]))
        dark_pixel_min = sum([x[0] for x in self.colors]) * self.light_ratio
        total = 0
        self.tolight = set()
        i = 0
        while total < dark_pixel_min:
            self.tolight.add(self.colors[i][1])
            i += 1
            total += self.colors[i][0]

    def filter_pixel(self, r, g, b, a):
        pixel = (0, 0, 0, 0)
        if self.isvisible((r, g, b, a)):
            pixel = (0, 0, 0, a)
            if (r, g, b, a) in self.tolight:
                pixel = (255, 255, 255, a)
        return pixel


DEFAULT_HUE = 329
DEFAULT_SATURATION_FILL = 0.5
DEFAULT_BRIGHTNESS_FILL = 0.5


def dyeimage(img, *args, **kwargs):
    LOG.info('Creating dyeimage for {0}...'.format(os.path.basename(img.filename)))
    d = DyeImage(img, *args, **kwargs)
    new_img = d.get_filtered()
    LOG.info('Finished creating dyeimage for {0}...'.format(os.path.basename(img.filename)))
    return new_img


class DyeImage(ImageFilter):

    def __init__(self, *args, **kwargs):
        self.hue = kwargs.pop("hue", DEFAULT_HUE)
        self.saturation_fill = kwargs.pop("saturation_fill", DEFAULT_SATURATION_FILL)
        self.brightness_fill = kwargs.pop("brightness_fill", DEFAULT_BRIGHTNESS_FILL)
        super(DyeImage, self).__init__(*args, **kwargs)

    def filter_pixel(self, r, g, b, a):
        h, s, v = rgb_to_hsv(r, g, b)
        ns = s + (1 - s) * self.saturation_fill
        nv = v + (255 - v) * self.brightness_fill
        nr, ng, nb = hsv_to_rgb(self.hue, ns, nv)
        na = self.fade(r, g, b, a)
        return (nr, ng, nb, na)

    def fade(self, r, g, b, a):
        return ((r + g + b) / (255 * 3))**0.25 * a
