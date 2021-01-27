# /usr/bin/env python

import tensorflow as tf

print('tensorflow: ', tf.__version__)

mobnet = tf.keras.applications.mobilenet

model = mobnet.MobileNet(weights='imagenet')

MODEL_SAVE_PATH = './predictor/mobilenet_saved_model/0001'
model.save(MODEL_SAVE_PATH, save_format='tf')
preprocessing = mobnet.preprocess_input
post_processing = mobnet.decode_predictions

print('model saved: {}'.format(MODEL_SAVE_PATH))
