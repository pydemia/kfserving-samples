from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from alibi.datasets import fetch_adult
from tensorflow.keras.applications.mobilenet import preprocess_input
from alibi.datasets import fetch_imagenet
import alibi
from alibi.explainers import AnchorImage
import dill
import tensorflow as tf
import numpy as np
import argparse

print('tensorflow: ', tf.__version__)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--model', '-m', type=str, required=True)

ARGS = parser.parse_args()
#MODEL_PATH = './mobilenet_saved_model/0001'
MODEL_PATH = ARGS.model


# model = tf.saved_model.load('../predictor/mobilenet_saved_model')
#model = tf.keras.models.load_model('../predictor/mobilenet_saved_model')
model = tf.keras.models.load_model(MODEL_PATH)

# PREDICT_TEMPLATE = 'http://{0}/v1/models/mobilenet-exp:predict'
# EXPLAIN_TEMPLATE = 'http://{0}/v1/models/mobilenet-exp:explain'


# def get_image_data():
#     data = []
#     image_shape = (224, 224, 3)
#     target_size = image_shape[:2]

#     image_url = "https://raw.githubusercontent.com/pydemia/containers/master/kubernetes/apps/kfserving/examples/mobilenet/elephant.jpg"
#     filename = image_url.split("/")[-1]
#     urllib.request.urlretrieve(image_url, filename)

#     image = Image.open(filename).convert('RGB')
#     image = np.expand_dims(image.resize(target_size), axis=0)
#     data.append(image)
#     data = np.concatenate(data, axis=0)
#     return data


# def predict(cluster_ip, hostname, img):
#     data = get_image_data()
#     images = preprocess_input(data)

#     payload = {
#         "instances": [images[0].tolist()]
#     }

#     # sending post request to TensorFlow Serving server
#     headers = {'Host': hostname}
#     url = PREDICT_TEMPLATE.format(cluster_ip)
#     print("Calling ", url)
#     r = requests.post(url, json=payload, headers=headers)
#     resp_json = json.loads(r.content.decode('utf-8'))
#     preds = np.array(resp_json["predictions"])
#     label = decode_predictions(preds, top=1)

#     # plt.imshow(data[0])
#     # plt.title(label[0])
#     # plt.show()

#     #im = Image.fromarray(preds)
#     im = Image.fromarray(data[0])
#     im.save("test_output_predict" + str(label) + ".jpg")
# predict(args.cluster_ip, args.hostname)

# data = get_image_data()
# images = preprocess_input(data)

# payload = {
#     "instances": [images[0].tolist()]
# }
# data_x = images[0].tolist()

def predictor(x): return model.predict(x)


def predictor(x): return model.predict(x).argmax()


kwargs = {'n_segments': 15, 'compactness': 20, 'sigma': .5}
image_shape = (224, 224, 3)

#explainer = alibi.explainers.AnchorTabular(predictor)
_adult = fetch_adult()
_data = _adult['data']
_target = _adult['target']
_feature_names = _adult['feature_names']
_target_names = _adult['target_names']
_category_map = _adult['category_map']
np.random.seed(0)
data_perm = np.random.permutation(np.c_[_data, _target])
data = data_perm[:, :-1]
labels = data_perm[:, -1]
idx = 30
X_train, Y_train = data[:idx, :], labels[:idx]
X_test, Y_test = data[idx + 1:, :], labels[idx + 1:]
ordinal_features = [x for x in range(
    len(_feature_names)) if x not in list(_category_map.keys())]
ordinal_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='median')),
                                      ('scaler', StandardScaler())])
categorical_features = list(category_map.keys())
categorical_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='median')),
                                          ('onehot', OneHotEncoder(handle_unknown='ignore'))])
preprocessor = ColumnTransformer(transformers=[('num', ordinal_transformer, ordinal_features),
                                               ('cat', categorical_transformer, categorical_features)])
# train an RF model
print("Train random forest model")
np.random.seed(0)
clf = RandomForestClassifier(n_estimators=50)
pipeline = Pipeline([('preprocessor', preprocessor),
                     ('clf', clf)])
pipeline.fit(X_train, Y_train)
print("Creating an explainer")


def predict_fn(x): return clf.predict(preprocessor.transform(x))


explainer_tab = alibi.explainers.AnchorTabular(predict_fn, _feature_names)


def predictor(x): return model.predict(x)


explainer = AnchorImage(
    predictor,
    image_shape,
    segmentation_fn='slic',
    segmentation_kwargs=kwargs,
    images_background=None,
)
explainer_tab.predict_fn
explainer_tab.predictor
explainer.predictor


def predictor(x): return model.predict(x).argmax(axis=1)


explainer = AnchorImage(
    predictor,
    image_shape,
    segmentation_fn='slic',
    segmentation_kwargs=kwargs,
    images_background=None,
)
explainer.predictor

categories = ['tusker', 'African elephant', 'Persian cat',
              'volcano', 'strawberry', 'jellyfish', 'centipede', ]
full_data = []
full_labels = []
for category in categories:
    data, labels = fetch_imagenet(
        category,
        nb_images=10,
        target_size=image_shape[:2],
        seed=0,
        return_X_y=True,
    )
    full_data.append(data)
    full_labels.append(labels)

full_data = np.concatenate(full_data, axis=0)
full_labels = np.concatenate(full_labels, axis=0)

images = preprocess_input(full_data)
print(images.shape)
train_x = images[0].tolist()
explainer.fit(
    train_x
)

# Clear explainer predict_fn as its a lambda and will be reset when loaded
print(explainer.predict_fn)
print(explainer.predictor)
explainer.predictor = None
with open("./explainer.dill", 'wb') as f:
    dill.dump(explainer, f)


# # %%
# import dill
# from alibiexplainer import AlibiExplainer
# from alibiexplainer.explainer import ExplainerMethod

# alibi_model = None
# with open("./explainer.dill", 'rb') as f:
#         #logging.info("Loading Alibi model")
#         alibi_model = dill.load(f)

# MODEL_NAME = 'mobilenet-exp'
# PREDICTOR_HOST = '127.0.0.1:8501'
# extra = {'batch_size': 1}

# explainer = AlibiExplainer(MODEL_NAME, # args.model_name,
#                            PREDICTOR_HOST, # args.predictor_host,
#                            ExplainerMethod.anchor_images, # ExplainerMethod(args.command),
#                            extra,
#                            alibi_model)

# from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
# import numpy as np
# import json
# import os
# from PIL import Image
# import urllib


# def get_image_data():
#     data = []
#     image_shape = (224, 224, 3)
#     target_size = image_shape[:2]
#     image_url = "https://raw.githubusercontent.com/pydemia/containers/master/kubernetes/apps/kfserving/examples/mobilenet/elephant.jpg"
#     filename = image_url.split("/")[-1]
#     urllib.request.urlretrieve(image_url, filename)
#     image = Image.open(filename).convert('RGB')
#     image = np.expand_dims(image.resize(target_size), axis=0)
#     data.append(image)
#     data = np.concatenate(data, axis=0)
#     return data


# data = get_image_data()
# images = preprocess_input(data)

# payload = {
#     "instances": [images[0].tolist()]
# }

# REQUEST = payload
# #explainer.explain(REQUEST)
# explainer.wrapper.anchors_image.explain(np.array(REQUEST['instances']))


# %%
