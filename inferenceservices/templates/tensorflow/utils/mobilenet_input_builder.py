#!/usr/bin/python3

import os
import json
import argparse
from PIL import Image
import base64
import cv2
import tensorflow as tf


def _load_image_as_str(
        filename, output,
        image_type='rgb', output_type='numpy',
        for_explainer=False,
        input_tensorname=None,
        ):

    filelist = filename.split(',')

    content_list = []
    for filename in filelist:

        if image_type == 'rgb':
            img_bgr = cv2.imread(filename, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        else:
            img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        # The inputs pixel values are scaled between -1 and 1, sample-wise.
        img = tf.keras.applications.mobilenet.preprocess_input(
            img,
            data_format='channels_last',
        )

        if output_type == 'b64':
            content = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
        elif output_type == 'numpy':
            content = img.tolist()
        # content = base64.b64encode(img).decode('utf8')

        if input_tensorname:
            content_item = {input_tensorname: content}
        else:
            content_item = content

        content_list += [content_item]

    # ====================================
    # `saved_model_cli` RESULT:
    # inputs['input_1'] tensor_info:
    #   dtype: DT_FLOAT
    #   shape: (-1, 224, 224, 3)
    #   name: serving_default_input_1: 0
    # ====================================
    # res = {
    #     "instances": [
    #         {"input_1": [content]},
    #         {"input_1": [content]}
    #     ]
    # }
    # res = {"instances": [content, content]}

    res = {"instances": content_list}

    # savepath = os.path.join(output, filename + '.json')
    savepath = output
    savepath_origin, ext = os.path.splitext(savepath)
    savepath_exp = ''.join([savepath_origin + '_for_explainer', ext])

    with open(savepath, 'w') as f:
        # json.dumps({"image": base64.b64encode(imdata).decode('ascii')})
        # json.dump(res, f, ensure_ascii=False)
        json.dump(res, f, ensure_ascii=False)
    print('saved:', savepath)

    if for_explainer:
        res_for_explain = {'instances': [content]}
        # savepath = os.path.join(output, filename + '.json')
        savepath = output
        with open(savepath_exp, 'w') as f:
            # json.dumps({"image": base64.b64encode(imdata).decode('ascii')})
            # json.dump(res, f, ensure_ascii=False)
            json.dump(res_for_explain, f, ensure_ascii=False)
        print('saved:', savepath_exp)


parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--input', '-i', type=str, required=True)
parser.add_argument('--input_type', '-it', type=str,
                    default='rgb', choices=['rgb', 'grayscale'])
parser.add_argument('--input_tensorname', '-t', type=str, default=None)
parser.add_argument('--output', '-o', type=str, required=True)
parser.add_argument('--output_type', '-ot', type=str, default='numpy', choices=['b64', 'numpy'])
parser.add_argument('--for_explainer', '-exp', type=bool,
                    default=False, choices=[True, False])


if __name__ == '__main__':
    ARGS = parser.parse_args()
    INPUT = ARGS.input
    INPUT_TYPE = ARGS.input_type
    INPUT_TENSORNAME = ARGS.input_tensorname
    OUTPUT = ARGS.output
    OUTPUT_TYPE = ARGS.output_type
    FOR_EXPLAINER = ARGS.for_explainer
    _load_image_as_str(
        INPUT,
        OUTPUT,
        image_type=INPUT_TYPE, output_type=OUTPUT_TYPE,
        for_explainer=FOR_EXPLAINER,
        input_tensorname=INPUT_TENSORNAME,
    )

"""
# Basic: {instances: [elephant_img_numpy]}
python mobilenet_input_builder.py \
    --input elephant.jpg \
    --output input_numpy.json \
    --output_type numpy

# Tensorname: {instances: [{"input_1": elephant_img_numpy}]}
python mobilenet_input_builder.py \
    --input elephant.jpg \
    --input_tensorname 'input_1' \
    --output input_numpy_tensorname.json \
    --output_type numpy


# Batch Input(A input with 2 images): {"instances": [elephant_img_numpy,squirrel_img_numpy]}
python mobilenet_input_builder.py \
    --input elephant.jpg,squirrel.jpg \
    --output input_numpy_multi_images.json \
    --output_type numpy


# Batch Input, Tensorname(A input with 2 images): {"instances": [{"input_1": elephant_img_numpy},{"input_1",squirrel_img_numpy}]}
python mobilenet_input_builder.py \
    --input elephant.jpg,squirrel.jpg \
    --input_tensorname 'input_1' \
    --output input_numpy_multi_images_tensorname.json \
    --output_type numpy
"""
