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
import tqdm
# ssl._create_default_https_context = ssl._create_unverified_context


def get_image_data_from_url(img_url=None):

    if img_url is None:
        img_url = "https://raw.githubusercontent.com/pydemia/containers/master/kubernetes/apps/kfserving/examples/mobilenet/elephant.jpg"
        print("using the default image: 'elephant.jpg'")

    data = []
    image_shape = (224, 224, 3)
    target_size = image_shape[:2]

    # filename = img_url.split("/")[-1]
    filename = os.path.basename(img_url)
    urllib.request.urlretrieve(img_url, filename)

    image = Image.open(filename).convert('RGB')
    image = np.expand_dims(image.resize(target_size), axis=0)
    data.append(image)
    data = np.concatenate(data, axis=0)
    return data, filename


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


# def predict(cluster_ip, hostname, model_name):
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


# def explain(cluster_ip, hostname, model_name):
#     data = get_image_data()
#     images = preprocess_input(data)

#     payload = {
#         "instances": [images[0].tolist()]
#     }

#     # sending post request to TensorFlow Serving server
#     headers = {'Host': hostname}
#     url = EXPLAIN_TEMPLATE.format(cluster_ip, model_name)
#     print("Calling ", url)
#     r = requests.post(url, json=payload, headers=headers)
#     if r.status_code == 200:
#         explanation = json.loads(r.content.decode('utf-8'))

#         exp_arr = np.array(explanation['anchor'])

#         # f, axarr = plt.subplots(1, 2)
#         # axarr[0].imshow(data[0])
#         # axarr[1].imshow(explanation['anchor'])
#         # plt.show()

#         #im = Image.fromarray(exp_arr)
#         im = Image.fromarray(explanation['anchor'])
#         im = im.convert("L")
#         im.save("test_output_explain.jpg")

#     else:
#         print("Received response code and content", r.status_code, r.content)


def request(img_url=None, cluster_ip=None, hostname=None, model_name=None, op='predict'):

    if (img_url is None) or (img_url.startswith('http')):
        data, filename = get_image_data_from_url(img_url)
        images = preprocess_input(data)
        payload = {
            "instances": [images[0].tolist()]
        }
    else:
        filename = os.path.basename(img_url)
        with open(img_url, 'r') as f:
            payload = json.load(f)

    RESTAPI_TEMPLATE = 'http://{0}/v1/models/{1}:{2}'

    # sending post request to TensorFlow Serving server
    headers = {'Host': hostname}
    url = RESTAPI_TEMPLATE.format(cluster_ip, model_name, op)
    print("Calling ", url)
    response = requests.post(url, json=payload, headers=headers)

    return response, op, filename


def save_raw_response(response, op, input_filename):

    filename, fileext = os.path.splitext(input_filename)
    SAVEPATH = f'{filename}_output.json'
    if response.status_code == 200:
        resp = json.loads(response.content.decode('utf-8'))

        with open(SAVEPATH, 'w') as f:
            json.dump(resp, f)
        print("{}: result saved: {}".format(op, SAVEPATH))

    else:
        print("Received response code and content", response.status_code, response.content)


def decode_response(response, op):
    if response.status_code == 200:
        resp = json.loads(response.content.decode('utf-8'))

        if op == 'predict':
            preds = np.array(resp["predictions"])
            # label = resp['pred_decode']
            label = decode_predictions(preds, top=1)

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
        print("Received response code and content", response.status_code, response.content)


def predict(
        img_url=None,
        cluster_ip=None, hostname=None, model_name=None,
):
    response, op, input_filename = request(
        img_url=img_url,
        cluster_ip=cluster_ip,
        hostname=hostname,
        model_name=model_name,
        op='predict',
    )
    # decode_response(response, op)
    save_raw_response(response, op, input_filename)


def explain(
        img_url=None,
        cluster_ip=None, hostname=None, model_name=None,
):
    resp_pred, _ = request(
        img_url=img_url,
        cluster_ip=cluster_ip,
        hostname=hostname,
        model_name=model_name,
        op='predict',
    )
    resp = json.loads(resp_pred.content.decode('utf-8'))
    # label = resp['pred_decode']
    label = decode_predictions(resp, top=1)
    print(label)
    response, op, input_filename = request(
        img_url=img_url,
        cluster_ip=cluster_ip,
        hostname=hostname,
        model_name=model_name,
        op='explain',
    )
    # decode_response(response, op)
    save_raw_response(response, op, input_filename)


# %%
parser = argparse.ArgumentParser()
# parser.add_argument('--is_url', default=False,
#                     help='DATA_FROM_URL_BOOL')
parser.add_argument('--img_url', default=None,
                    help='IMG_URL')
parser.add_argument('--cluster_ip', default=os.environ.get("CLUSTER_IP"),
                    help='Cluster IP of Istio Ingress Gateway')
parser.add_argument('--hostname', default=os.environ.get("SERVICE_HOSTNAME"),
                    help='SERVICE_HOSTNAME')
parser.add_argument('--model_name', default=os.environ.get("MODEL_NAME"),
                    help='MODEL_NAME')
parser.add_argument('--op', choices=["predict", "explain"], default="predict",
                    help='Operation to run')
args, _ = parser.parse_known_args()


OP = args.op
IMG_URL = args.img_url
CLUSTER_IP = args.cluster_ip
HOSTNAME = args.hostname
MODEL_NAME = args.model_name


# OP = 'explain'
# IMG_URL = None
# CLUSTER_IP = '104.198.233.27'
# HOSTNAME = 'mobilenet-fullstack.ifsvc.104.198.233.27.xip.io'
# MODEL_NAME = 'mobilenet-fullstack'

# img_url = None
# cluster_ip = CLUSTER_IP
# hostname = HOSTNAME
# model_name = MODEL_NAME

if __name__ == "__main__":

    if OP == "predict":
        predict(
            img_url=IMG_URL,
            cluster_ip=CLUSTER_IP,
            hostname=HOSTNAME,
            model_name=MODEL_NAME,
        )
    elif OP == "explain":
        explain(
            img_url=IMG_URL,
            cluster_ip=CLUSTER_IP,
            hostname=HOSTNAME,
            model_name=MODEL_NAME,
        )

"""
python test_inference.py \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

python test_inference.py \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op explain
"""


"""
python test_inference.py \
    --img_url input_numpy.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

python test_inference.py \
    --img_url input_numpy_tensorname.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

python test_inference.py \
    --img_url input_numpy_multi_images.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

python test_inference.py \
    --img_url input_numpy_multi_images_tensorname.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

"""
# %%
