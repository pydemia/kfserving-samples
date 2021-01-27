import kfserving
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
import logging
import numpy as np
import pandas as pd
import os
import json
import argparse
import cv2

import base64
from io import BytesIO

import collections
import itertools as it

import tensorflow as tf
logging.info('tensorflow: {}'.format(tf.__version__))


def depth(iterable):
    assert isinstance(iterable, collections.Iterable), 'Not an Iterable.'
    container = iterable
    depth = 0
    shape = str(len(container))
    while True:
        try:
            if isinstance(container, dict):
                container = iter(container.values())
            elif isinstance(container, str):
                depth += 1
                shape += ', {}'.format(len(container))
                raise TypeError
            else:
                container = iter(container)
            element = next(container)
            depth += 1
            shape += ', {}'.format(len(element))
            container = element

        except TypeError:
            break

    return depth, '({})'.format(shape)


logging.basicConfig(level=kfserving.constants.KFSERVING_LOGLEVEL)


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


def _serialize(jsonlike_dict):
    return json.loads(json.dumps(jsonlike_dict, cls=NumpyEncoder))


def _check_shape(obj):
    if hasattr(obj, 'shape'):
        return '[{}] {}'.format('shape', obj.shape)
    elif hasattr(obj, '__len__'):
        return '[{}] {}'.format('len', depth(obj)[-1])
    elif isinstance(obj, JpegImageFile) and hasattr(obj, '_size'):
        return '[{}] {}, {}'.format('size', obj._size, obj.mode)
    else:
        return '[{}] {}'.format('raw', '')


# Preprocessing -----------------------------
def _load_b64_string_to_pil_img(b64_byte_string):
    image_bytes = base64.b64decode(b64_byte_string)
    image_data = BytesIO(image_bytes)
    img = Image.open(image_data)
    return img


def preprocess_fn(instance):
    # logging.info('preprocess_fn:input: type:{} shape:{}'.format(
    #     type(instance), _check_shape(instance)
    # ))

    # For prediction, `instance` must contain the real input only.
    img_array = np.array(instance)  # instance['input_1']

    # img = _load_b64_string_to_pil_img(instance)  # instance['input_1']
    # img_resized = img.resize([224, 224], resample=Image.BILINEAR)
    # img_array = tf.keras.preprocessing.image.img_to_array(img_resized)

    # The inputs pixel values are scaled between -1 and 1, sample-wise.
    img_prep = tf.keras.applications.mobilenet.preprocess_input(
        img_array,
        data_format='channels_last',
    )
    img = cv2.resize(img_prep, (224, 224), interpolation=cv2.INTER_CUBIC)
    x = img.tolist()
    # logging.info('preprocess_fn:output: type: {} shape: {}'.format(
    #     type(x), _check_shape(x)
    # ))
    # x = x.tolist()  # _serialize(x)
    return x


# Postprocessing ----------------------------
def postprocess_fn(pred):
    logging.info('postprocess_fn:input: type: {} shape: {}'.format(
        type(pred), _check_shape(pred)
    ))
    pred_array = np.array(pred)
    # if len(pred_array.shape) < 2:
    #   pred_array = np.expand_dims(pred_array, axis=0)
    decoded = tf.keras.applications.mobilenet.decode_predictions(
        pred_array,
        top=2,
    )
    logging.info('postprocess_fn:output: type: {} shape: {}'.format(
        type(decoded), _check_shape(decoded)
    ))
    return decoded


class ImageTransformer(kfserving.KFModel):
    def __init__(self, name: str, predictor_host: str):
        super().__init__(name)
        self.predictor_host = predictor_host

    def preprocess(self, inputs):
        logging.info('preprocess:input: type: {} shape: {}'.format(
            type(inputs['instances']), _check_shape(inputs['instances'])
        ))
        prep = [preprocess_fn(i) for i in inputs['instances']]
        logging.info('preprocess:input: type: {} shape: {}'.format(
            type(prep), _check_shape(prep)
        ))
        res = {
            'instances': prep,
        }
        logging.info('preprocess:output: type: {} shape: {}'.format(
            type(res), _check_shape(res)
        ))
        return res

    def postprocess(self, outputs):
        # outputs: {"predictions": ndarray_as_list}
        # return outputs
        logging.info('postprocess:input: type: {} shape: {}'.format(
            type(outputs), _check_shape(outputs)
        ))
        logging.info(outputs.keys())
        res = {
            'predictions': outputs['predictions'],
            'pred_decode': postprocess_fn(outputs['predictions']),
        }
        logging.info('postprocess:output: type: {} shape: {}'.format(
            type(res), _check_shape(res)
        ))
        # logging.info(res)
        return res


parser = argparse.ArgumentParser(parents=[kfserving.kfserver.parser])
parser.add_argument(
    '--model_name', default='model',
    help='The name that the model is served under.',
)
parser.add_argument(
    '--predictor_host',
    required=True,
    help='The URL for the model predict function',
)
args, _ = parser.parse_known_args()


if __name__ == "__main__":
    transformer = ImageTransformer(
        args.model_name,
        predictor_host=args.predictor_host,
    )
    kfserver = kfserving.KFServer()
    kfserver.start(models=[transformer])
