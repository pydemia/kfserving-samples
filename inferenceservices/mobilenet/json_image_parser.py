#!/usr/bin/python3

import os
import json
import argparse

import base64
from io import BytesIO
import cv2
from PIL import Image
import numpy as np




def _load_b64_string_to_img(b64_byte_string):
    image_bytes = base64.b64decode(b64_byte_string)
    image_data = BytesIO(image_bytes)
    img = Image.open(image_data)
    return img


def _load_json_as_image(filename, output, type='rgb'):
    # with open(filename, 'r') as f:
    #     result_list = json.load(f)
    
    # for result in result_list:
    #     # image_byte_string = result['image']
    #     # image_bytes = base64.b64decode(image_byte_string)
    #     # image_data = BytesIO(image_bytes)
    #     # img = Image.open(image_data)
        
    #     #img = _load_b64_string_to_img(result['image'])
    #     output_name = output + '_' + result['key'] + '.jpg'
    #     img.save(output_name)
    
    with open(filename, 'r') as f:
        result = json.load(f)

    #img = _load_b64_string_to_img(result['predictions'])
    img_array = np.array(result['predictions'])
    img = Image.fromarray(img_array, 'RGB')
    output_name = output + '_' + '.jpg'
    img.save(output_name)

    print('saved:', output)

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--input', '-i', type=str, required=True)
parser.add_argument('--output', '-o', type=str, required=True)


if __name__ == '__main__':
    ARGS = parser.parse_args()
    INPUT = ARGS.input
    OUTPUT = ARGS.output
    _load_json_as_image(INPUT, OUTPUT)
