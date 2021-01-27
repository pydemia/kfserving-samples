from PIL import Image
import logging
import numpy as np
import os
import json
import argparse

import base64
from io import BytesIO
import tensorflow as tf
print('tensorflow: ', tf.__version__)

# mobnet = tf.keras.applications.mobilenet
# pre_processing_fn = mobnet.preprocess_input
# post_processing_fn = mobnet.decode_predictions

# model = mobnet.MobileNet(weights='imagenet')
# model.save('./mobilenet_saved_model', save_format='tf')

# image_saved_path = tf.keras.utils.get_file(
#     "grace_hopper.jpg",
#     "https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg",
# )


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):   # pylint: disable=arguments-differ,method-hidden
        if isinstance(obj, (
                np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8,
                np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def _load_b64_string_to_img(b64_byte_string):
    image_bytes = base64.b64decode(b64_byte_string)
    image_data = BytesIO(image_bytes)
    img = Image.open(image_data)
    return img


def preprocess_fn(instance):
    img = _load_b64_string_to_img(instance['input_1'])
    img_resized = img.resize([224, 224], resample=Image.BILINEAR)
    img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
    # The inputs pixel values are scaled between -1 and 1, sample-wise.
    x = tf.keras.applications.mobilenet.preprocess_input(
        img_array,
        data_format='channels_last',
    )
    #x = np.expand_dims(x, axis=0)
    return x


# Postprocessing ----------------------------
def postprocess_fn(pred):
    pred_array = np.array(pred)
    if len(pred_array.shape) < 2:
      pred_array = np.expand_dims(pred_array, axis=0)
    decoded = tf.keras.applications.mobilenet.decode_predictions(
        pred_array, top=5
    )
    #logging.info(decoded)
    return decoded
