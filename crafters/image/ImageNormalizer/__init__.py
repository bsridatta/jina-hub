__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Tuple, Dict, Union, Iterable

import numpy as np

from jina.executors.decorators import single
from jina.executors.crafters import BaseCrafter

from .helper import _load_image, _move_channel_axis, _crop_image, _resize_short


class ImageNormalizer(BaseCrafter):
    """
    Normalize the image.

    :class:`ImageNormalizer` works on doc-level,
        it receives values of file names on the
        doc-level and returns image matrix on the chunk-level

    :param target_size: Desired output size. If size is a sequence
        like (h, w), the output size will be matched to this.
        If size is an int, the smaller edge of the image will be matched
        to this number maintaining the aspect ratio.
    :param img_mean: The mean of the images in `RGB` channels.
        Set to `[0.485, 0.456, 0.406]` for the models trained
        on `imagenet` with pytorch backbone.
    :param img_std: the std of the images in `RGB` channels.
        Set to `[0.229, 0.224, 0.225]` for the models trained
        on `imagenet` with pytorch backbone.
    :param resize_dim: the size of images' height and width to be resized to.
        The images are resized before cropping to the output size
    :param channel_axis: the axis id of the color channel,
        ``-1`` indicates the color channel info at the last axis
    :param target_channel_axis: the axis id of the color channel that need to move to,
        ``-1`` indicates the color channel info at the last axis, and ``0`` indicates the first axis
    """

    def __init__(self,
                 target_size: Union[Iterable[int], int] = 224,
                 img_mean: Tuple[float] = (0, 0, 0),
                 img_std: Tuple[float] = (1, 1, 1),
                 resize_dim: int = 256,
                 channel_axis: int = -1,
                 target_channel_axis: int = -1,
                 *args,
                 **kwargs):
        """Set Constructor."""
        super().__init__(*args, **kwargs)
        if isinstance(target_size, int):
            self.target_size = target_size
        elif isinstance(target_size, Iterable):
            self.target_size = tuple(target_size)
        else:
            raise ValueError(f'target_size {target_size} should be an integer or tuple/list of 2 integers')
        self.resize_dim = resize_dim
        self.img_mean = np.array(img_mean).reshape((1, 1, 3))
        self.img_std = np.array(img_std).reshape((1, 1, 3))
        self.channel_axis = channel_axis
        self.target_channel_axis = target_channel_axis

    @single
    def craft(self, blob: 'np.ndarray', *args, **kwargs) -> Dict:
        """
        Normalize the image.

        :param blob: the ndarray of the image with the color channel at the last axis
        :return: a chunk dict with the normalized image
        """
        # load the data with original channel_axis
        raw_img = _load_image(blob, self.channel_axis)
        _img = self._normalize(raw_img)
        # move the channel_axis to target_channel_axis to better fit different models
        img = _move_channel_axis(_img, -1, self.target_channel_axis)
        return dict(offset=0, blob=img)

    def _normalize(self, img):
        img = _resize_short(img, target_size=self.resize_dim)
        img, _, _ = _crop_image(img, target_size=self.target_size, how='center')
        img = np.array(img).astype('float32')/255
        img -= self.img_mean
        img /= self.img_std
        return img
