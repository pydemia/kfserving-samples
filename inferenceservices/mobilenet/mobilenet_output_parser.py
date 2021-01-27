#!/usr/bin/python3

import os
import json
import argparse
from PIL import Image
import base64
import cv2
import tensorflow as tf

import matplotlib.pyplot as plt


def show_img(img_arr, savepath=None):
  _img = np.array(img_arr)
  xmax, ymax = _img.shape[:2]
  fig, ax = plt.subplots(nrows=1, ncols=1)
  ax.set_axis_off()
  ax.imshow(_img, aspect='equal', extent=[0, xmax, ymax, 0]).get_extent()

  if savepath:
    os.makedirs(savepath, exist_ok=True)
    fig.savefig(savepath)


parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--input', '-i', type=str, required=True)
parser.add_argument('--input_type', '-it', type=str,
                    default='rgb', choices=['rgb', 'grayscale'])
parser.add_argument('--output', '-o', type=str, required=True)
parser.add_argument('--output_type', '-ot', type=str,
                    default='numpy', choices=['b64', 'numpy'])
parser.add_argument('--for_explainer', '-exp', type=bool,
                    default=False, choices=[True, False])


RESP_JSON_PATH="./logs/output_explain.json"

with open(RESP_JSON_PATH, 'r') as f:
  resp = json.load(f)


print(resp.keys())
# dict_keys(['anchor', 'segments', 'precision', 'coverage', 'raw', 'meta'])

explainer_typ = resp['meta']['name']
resp['raw'].keys()

resp['anchor']     # Superpixels in the anchor (Most wanted) (image array)
resp['segments']   # Visualize all the superpixels as grid   (image array)

show_img(resp['anchor'])

show_img(resp['segments'])

# alibi.explainers.anchor_explanation.AnchorExplanation.precision
# Anchor precision for the given partial_index: Get the result precision until a certain index.
# For example, if the result has precisions[0.1, 0.5, 0.95] and partial_index = 1, this will return 0.5.
resp['precision']  # Anchor precision (float, 0.0 ~ 1.0)

resp['coverage']   # Anchor coverage (float, 0.0 ~ 1.0)

resp['raw']        # Anchor All history

resp['raw'].keys()
# dict_keys([
# 'feature', 'mean', 'precision', 'coverage', 'examples',
# 'all_precision', 'num_preds', 'instance', 'prediction'])

# segment_labels: Features used in the result conditions.
resp['raw']['feature']
resp['raw']['mean']
resp['raw']['precision']
resp['raw']['coverage']
resp['raw']['examples'][0].keys()
# dict_keys(['covered',
# 'covered_true', 'covered_false',
# 'uncovered_true', 'uncovered_false'])

resp['raw']['examples'][0]['covered']
# resp['raw']['examples'][0]['covered_true']
# resp['raw']['examples'][0]['covered_false']
# resp['raw']['examples'][0]['uncovered_true']
# resp['raw']['examples'][0]['uncovered_false']


fig, axes = plt.subplots(nrows=10, ncols=1, figsize=(20*10, 20))
for _, ax in zip(resp['raw']['examples'][0]['covered'], axes.ravel()):
  ax.imshow(_, aspect='equal')
  ax.set_axis_off()
fig.tight_layout(rect=[0, 0.02, 1, 0.97])
fig.suptitle('tried_segments', y=0.98, horizontalalignment='center')


resp['raw']['num_preds']  # 130001

resp['raw']['instance']  # Original input image (image array)


show_img(resp['raw']['instance'])

resp['raw']['prediction']  # Predictor output(or Transformer postprocess output)


fig, axes = plt.subplots(nrows=1, ncols=3)

explain_score = 'coverage: {0}, precision: {1}'.format(resp['coverage'], resp['precision'])
img_labels = ['input', 'superpixel', 'segment_grid']
img_scores = [resp['raw']['prediction'], explain_score, ]
img_outputs = [resp['raw']['instance'], resp['anchor'], resp['segments']]
for ax, _img, _label, _score in zip(axes.ravel(), img_outputs, img_labels):
  ax.set_axis_off()
  ax.imshow(_img, aspect='equal')
  ax.set_title(_label)
