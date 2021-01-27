import argparse
import matplotlib.pyplot as plt
from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
from alibi.datasets import fetch_imagenet
import numpy as np
import requests
import json
import os
from PIL import Image
import ssl
import urllib


import asyncio
import aiohttp

import tqdm


def get_image_data(img_url=None):

    if img_url is None:
        img_url = "https://raw.githubusercontent.com/pydemia/containers/master/kubernetes/apps/kfserving/examples/mobilenet/elephant.jpg"
        filename = img_url.split("/")[-1]
        print(f"using the default image: '{filename}'")
    else:
        filename = img_url.split("/")[-1]
        print(f"using the given image: '{filename}'")

    urllib.request.urlretrieve(img_url, filename)

    data = []
    image_shape = (224, 224, 3)
    target_size = image_shape[:2]

    image = Image.open(filename).convert('RGB')
    image = np.expand_dims(image.resize(target_size), axis=0)
    data.append(image)
    data = np.concatenate(data, axis=0)
    return data


def show_img(img_arr, title=None, savepath=None):
    _img = np.array(img_arr)
    xmax, ymax = _img.shape[:2]
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.set_axis_off()
    ax.imshow(_img, aspect='equal', extent=[0, xmax, ymax, 0]).get_extent()
    ax.set_title(title)

    if savepath:
        dirpath = os.path.dirname(savepath)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        fig.savefig(savepath)


def decode_response(response, op):
    if response.status_code == 200:
        resp = json.loads(response.content.decode('utf-8'))

        if op == 'predict':
            preds = np.array(resp["predictions"])
            label = resp['pred_decode']
            # label = decode_predictions(preds, top=1)

            SAVEPATH = 'output_predict.jpg'
            show_img(preds, title=str(label), savepath=SAVEPATH)
            print("{}: result saved: {}".format(op, SAVEPATH))

        elif op == 'explain':

            model_input_img = resp['raw']['instance']
            model_output = resp['raw']['prediction']
            # pred = model_output['predictions']
            # label = model_output['pred_decode'][1:]
            label = model_output
            # label = decode_predictions(model_output['predictions'], top=1)[1:]

            explainer_typ = resp['meta']['name']
            exp_superpixels = resp['anchor']
            exp_segment_grid = resp['segments']
            exp_tried_seg = resp['raw']['examples'][0]['covered']
            exp_scores = {k: v for k, v in resp.items() if k in [
                'coverage', 'precision']}

            # show_img(model_input_img, savepath=None)
            # show_img(exp_superpixels, savepath=None)
            # show_img(exp_segment_grid, savepath=None)

            show_img(resp['segments'])

            explain_score = 'c: {0}, p: {1}'.format(
                resp['coverage'], resp['precision'])
            img_labels = [
                '\n'.join(['input', str(label)]),
                '\n'.join(['superpixel', explain_score]),
                '\n'.join(['segment_grid', explain_score]),
            ]
            img_outputs = [model_input_img, exp_superpixels, exp_segment_grid]

            fig, axes = plt.subplots(nrows=1, ncols=3)
            for ax, _img, _label in zip(axes.ravel(), img_outputs, img_labels):
                ax.set_axis_off()
                ax.imshow(_img, aspect='equal')
                ax.set_title(_label)

            SAVEPATH = 'output_explain.jpg'
            fig.savefig(SAVEPATH)
            print("{}: result saved: {}".format(op, SAVEPATH))

            # # (Optional) Tried segments
            # fig, axes = plt.subplots(nrows=10, ncols=1, figsize=(20*10, 20))
            # for _, ax in zip(resp['raw']['examples'][0]['covered'], axes.ravel()):
            #     ax.imshow(_, aspect='equal')
            #     ax.set_axis_off()
            #     fig.tight_layout(rect=[0, 0.02, 1, 0.97])
            #     fig.suptitle('tried_segments', y=0.98, horizontalalignment='center')

    else:
        print("Received response code and content",
              resp.status_code, resp.content)

    return fig
