from ai_modeling_hemorrhage import model

import tensorflow as tf
from distutils.version import LooseVersion, StrictVersion


# model_path = "/mnt/g/etc/test/model/epoch-260"  # Model Path
# seg_img, labels = hem.inference(model_path, images)

MODEL_PATH = './model/epoch-260'
model.load_weights(MODEL_PATH)

SAVEDMODEL_H5_PATH = '/tmp/saved_model.h5'
SAVEDMODEL_TF_PATH = '/tmp/saved_model'

# IF Tensorflow >= 2.x
if LooseVersion(tf.__version__) >= LooseVersion("2.0"):
    model.save(SAVEDMODEL_H5_PATH, format='h5')
    model.save(SAVEDMODEL_TF_PATH, format='tf')
else:
    # IF Tensorflow <= 1.x
    model.save(SAVEDMODEL_H5_PATH, save_format='h5')
    model.save(SAVEDMODEL_TF_PATH, save_format='tf')
