# %%
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
# ssl._create_default_https_context = ssl._create_unverified_context

# https://github.com/kubeflow/kfserving/blob/master/python/kfserving/kfserving/kfmodel.py
PREDICTOR_URL_FORMAT = "http://{0}/v1/models/{1}:predict"
EXPLAINER_URL_FORMAT = "http://{0}/v1/models/{1}:explain"


def get_image_data():
    data = []
    image_shape = (224, 224, 3)
    target_size = image_shape[:2]

    image_url = "https://raw.githubusercontent.com/pydemia/containers/master/kubernetes/apps/kfserving/examples/mobilenet/elephant.jpg"
    filename = image_url.split("/")[-1]
    urllib.request.urlretrieve(image_url, filename)

    image = Image.open(filename).convert('RGB')
    image = np.expand_dims(image.resize(target_size), axis=0)
    data.append(image)
    data = np.concatenate(data, axis=0)
    return data


def predict(cluster_ip, model_name, hostname):
    data = get_image_data()
    images = preprocess_input(data)

    payload = {
        "instances": [images[0].tolist()]
    }

    # sending post request to TensorFlow Serving server
    headers = {'Host': hostname}
    url = PREDICTOR_URL_FORMAT.format(cluster_ip, model_name)
    print("Calling ", url)
    r = requests.post(url, json=payload, headers=headers)
    print(r.content)
    resp_json = json.loads(r.content.decode('utf-8'))
    preds = np.array(resp_json["predictions"])
    label = decode_predictions(preds, top=1)

    im = Image.fromarray(data[0])
    im.save("test_explainer_local_output_predict" + str(label) + ".jpg")

    result = {
        'request': payload,
        'response': resp_json,
    }
    with open('test_explainer_local_output_predict.json', 'w') as f:
        json.dump(result, f)


def explain(cluster_ip, model_name, hostname):
    data = get_image_data()
    images = preprocess_input(data)

    payload = {
        "instances": [images[0].tolist()]
    }

    # sending post request to TensorFlow Serving server
    headers = {'Host': hostname}
    url = EXPLAINER_URL_FORMAT.format(cluster_ip, model_name)
    print("Calling ", url)
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 200:
        explanation = json.loads(r.content.decode('utf-8'))

        # im = Image.fromarray(explanation['anchor'])
        # im = im.convert("L")
        # im.save("test_output_explain.jpg")
        result = {
            'request': payload,
            'response': explanation,
        }
        with open('test_explainer_local_output_explain.json', 'w') as f:
            json.dump(result, f)

    else:
        print("Received response code and content", r.status_code, r.content)


parser = argparse.ArgumentParser()
parser.add_argument('--cluster_ip', default=os.environ.get("CLUSTER_IP"),
                    help='Cluster IP of Istio Ingress Gateway')
parser.add_argument('--hostname', default=os.environ.get("SERVICE_HOSTNAME"),
                    help='SERVICE_HOSTNAME')
parser.add_argument('--model_name', default=os.environ.get("MODEL_NAME"),
                    help='MODEL_NAME')
parser.add_argument('--op', choices=["predict", "explain"], default="predict",
                    help='Operation to run')
args, _ = parser.parse_known_args()

if __name__ == "__main__":
    if args.op == "predict":
        predict(args.cluster_ip, args.model_name, args.hostname)
    elif args.op == "explain":
        explain(args.cluster_ip, args.model_name, args.hostname)


# %%
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
