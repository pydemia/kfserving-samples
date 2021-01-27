from alibi.datasets import fetch_imagenet
import alibi
from alibi.explainers import AnchorImage
import dill
import tensorflow as tf
import numpy as np
import argparse
import joblib


print('tensorflow: ', tf.__version__)

# IN DOCKER-alibiexplainer:/mnt/models;
# python create_explainer_dill.py -m ./mobilenet_saved_model/0001

# IN LOCAL:mobilenet
# gsutil -m cp -r ./explainer/explainer.dill gs://yjkim-models/kfserving/mobilenet/explainer/explainer.dill
# aws s3 cp ./explainer/explainer.dill s3://yjkim-models/kfserving/mobilenet/explainer/explainer.dill


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--model', '-m', type=str, required=True)
parser.add_argument('--output', '-o', type=str, default='./explainer/explainer.dill')

ARGS = parser.parse_args()

MODEL_PATH = ARGS.model  # './predictor/mobilenet_saved_model/0001'
OUTPUT = ARGS.output

model = tf.keras.models.load_model(MODEL_PATH)

predict_fn = lambda x: model.predict(x)
seqment_fn = 'slic'
kwargs = {'n_segments': 15, 'compactness': 20, 'sigma': .5}
image_shape = (224, 224, 3)

explainer = AnchorImage(
    predict_fn,
    image_shape,
    segmentation_fn=seqment_fn,
    segmentation_kwargs=kwargs,
    images_background=None,
)

# Clear explainer predict_fn as its a lambda and will be reset when loaded
explainer.predict_fn = None
explainer.predictor = None

with open(OUTPUT, 'wb') as f:
    dill.dump(explainer, f)
# joblib.dump(model, 'model.joblib')

# %% --------------------------------------------------
# with open("./explainer.dill", 'rb') as f:
#     explainer = dill.load(f)

# categories = ['tusker', 'African elephant', 'Persian cat',
#               'volcano', 'strawberry', 'jellyfish', 'centipede', ]
# full_data = []
# full_labels = []
# for category in categories:
#     data, labels = fetch_imagenet(
#         category,
#         nb_images=10,
#         target_size=image_shape[:2],
#         seed=0,
#         return_X_y=True,
#     )
#     full_data.append(data)
#     full_labels.append(labels)

# full_data = np.concatenate(full_data, axis=0)
# full_labels = np.concatenate(full_labels, axis=0)
# from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input
# images = preprocess_input(full_data)
# print(images.shape)
# #train_x = images.tolist()
# # explainer.fit(
# #     train_x
# # )
