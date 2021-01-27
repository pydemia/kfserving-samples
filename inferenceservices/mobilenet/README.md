# KFServing with MobileNet

* `transformer-preprocessing`
* `predictor`
* `transformer-postprocessing`
* `explainer`

---

## Predictor

### Get SavedModel

```sh
$ python get_saved_model.py

tensorflow:  1.15.2
...
model saved: ./predictor/mobilenet_saved_model/0001
```

### Get informed

* Input: `input_1`
* Output: `act_softmax`

```sh
$ cd predictor/mobilenet_saved_model
$ saved_model_cli show --dir . \
  --tag_set serve --signature_def serving_default

...
The given SavedModel SignatureDef contains the following input(s):
  inputs['input_1'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 224, 224, 3)
      name: serving_default_input_1:0
The given SavedModel SignatureDef contains the following output(s):
  outputs['act_softmax'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 1000)
      name: StatefulPartitionedCall:0
Method name is: tensorflow/serving/predict
```

## Transformer

### Create a transformer for pre-processing and post-processing

`transformer/mobilenet_transformer.py`

### Build `transformer.Dockerfile`
```sh
docker build -t pydemia/mobilenet_transformer:latest \
  -f ./transformer/transformer.Dockerfile ./transformer/

TRANSFORMER_VERSION="tf1.15.2-0.2.0"
docker tag \
    pydemia/mobilenet_transformer:latest \
    pydemia/mobilenet_transformer:$TRANSFORMER_VERSION

docker tag \
    pydemia/mobilenet_transformer:$TRANSFORMER_VERSION \
    gcr.io/ds-ai-platform/mobilenet_transformer:$TRANSFORMER_VERSION

docker push \
    gcr.io/ds-ai-platform/mobilenet_transformer:$TRANSFORMER_VERSION
docker push \
    pydemia/mobilenet_transformer:$TRANSFORMER_VERSION

```

## Explainer

:warning: In `alibi >= 0.4.0`, Method has been changed: `predict_fn` -> `predictor`. We will build a tunned(`alias: self.predict_fn=self.predictor`) image.

### Build a proper container image(avoiding the alibi version issue)

```sh
cd mobilenet/explainer
ALIBIEXPLAINER_VERSION="v0.3.2-predict_fn"
#ALIBIEXPLAINER_VERSION="v0.4.0-predict_fn"

docker build \
    -t pydemia/alibiexplainer:latest -f "alibiexplainer-$ALIBIEXPLAINER_VERSION.Dockerfile" .

docker tag \
    pydemia/alibiexplainer:latest \
    pydemia/alibiexplainer:$ALIBIEXPLAINER_VERSION

docker tag \
    pydemia/alibiexplainer:$ALIBIEXPLAINER_VERSION \
    gcr.io/ds-ai-platform/alibiexplainer:$ALIBIEXPLAINER_VERSION

docker push \
    gcr.io/ds-ai-platform/alibiexplainer:$ALIBIEXPLAINER_VERSION
docker push \
    pydemia/alibiexplainer:$ALIBIEXPLAINER_VERSION

gsutil -m cp -r ./explainer/explainer.dill gs://yjkim-models/kfserving/mobilenet/explainer/explainer.dill

aws s3 cp ./explainer/explainer.dill s3://yjkim-models/kfserving/mobilenet/explainer/explainer.dill

cd ..
```

### Create `explainer.dill` inside the container

```sh
ALIBIEXPLAINER_IMAGE="docker.io/pydemia/alibiexplainer"
ALIBIEXPLAINER_VERSION="v0.3.2-predict_fn"

docker run --rm -it \
    --name exp_env \
    --entrypoint /bin/bash \
    -w /mnt/models \
    --mount src="$(pwd)",target=/mnt/models,type=bind \
    $ALIBIEXPLAINER_IMAGE:$ALIBIEXPLAINER_VERSION

# IN DOCKER: `exp_env:/mnt/models`
python create_explainer_dill.py \
  --model predictor/mobilenet_saved_model/0001 \
  --output explainer/explainer.dill

```

* Upload to GCP

```sh
# Predictor: tensorflow/serving:1.15.2
gsutil -m cp -r ./predictor/mobilenet_saved_model gs://yjkim-models/kfserving/mobilenet/predictor/

# Transformer: custom container
docker push gcr.io/ds-ai-platform/mobilenet_transformer:$TRANSFORMER_VERSION

# Exaplainer: alibi: type:AnchorImages
gsutil -m cp -r ./explainer/explainer.dill gs://yjkim-models/kfserving/mobilenet/explainer/explainer.dill
```

* Upload to AWS & Docker Hub
```sh
# Predictor: tensorflow/serving:1.15.2
aws s3 cp --recursive ./predictor/mobilenet_saved_model s3://yjkim-models/kfserving/mobilenet/predictor/mobilenet_saved_model

# Transformer: custom container
docker push docker.io/pydemia/mobilenet_transformer:$TRANSFORMER_VERSION

# Exaplainer: alibi: type:AnchorImages
aws s3 cp ./explainer/explainer.dill s3://yjkim-models/kfserving/mobilenet/explainer/explainer.dill
```

---

## Change current settings

```sh
$ kubectl -n kfserving-system get cm inferenceservice-config -o jsonpath='{.data.explainers}'
{
    "alibi": {
        "image" : "gcr.io/kfserving/alibi-explainer",
        "defaultImageVersion": "v0.3.0",
        "allowedImageVersions": [
           "v0.3.0"
        ]
    }
}

```

```sh
$ kubectl -n kfserving-system patch configmap/inferenceservice-config \
    --type merge -p "$(cat explainer-patch-inferenceservice-config.yaml)"

configmap/inferenceservice-config patched
```

## Depoly

```sh
INFERENCE_NS="ifsvc"
kubectl -n $INFERENCE_NS apply -f mobilenet-fullstack.yaml
# kubectl -n $INFERENCE_NS delete -f mobilenet-fullstack.yaml
```

## Test: `POST`

### Create an input: `json` format, containing `numpy`
```sh
$ python -m mobilenet_input_builder \
    -i ./elephant.jpg \
    -o ./input_numpy.json \
    -ot numpy

saved: ./input_numpy.json
```

```sh
INFERENCE_NS="ifsvc"
MODEL_NAME="mobilenet-fullstack"  # mobilenet, transformer, explainer
INPUT_PATH="@./input_numpy.json"

kubectl -n $INFERENCE_NS wait \
    --for=condition=ready --timeout=90s\
    inferenceservice $MODEL_NAME
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "
CLUSTER_IP: $CLUSTER_IP
HOSTNAME  : $SERVICE_HOSTNAME"

```

Then, the message would be the following:

```ascii
inferenceservice.serving.kubeflow.org/mobilenet-fullstack condition met

CLUSTER_IP: 104.198.233.27
HOSTNAME  : mobilenet-fullstack.ifsvc.104.198.233.27.xip.io
```

```sh
# PREDICTION
curl -v -H "Host: ${SERVICE_HOSTNAME}" \
  http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict \
  -d $INPUT_PATH > ./logs/output_predict.json

# EXPLANATION
# BUG: env_var not working
curl -v \
  --max-time 600 \
  --connect-timeout 600 \
  -H "Host: ${SERVICE_HOSTNAME}" \
  http://104.198.233.27/v1/models/mobilenet-fullstack:explain \
  -d $INPUT_PATH > ./logs/output_explain.json

```

In log, 

* Get Logs

```sh
INFERENCE_NS="ifsvc"
MODEL_NAME="mobilenet-fullstack"  # mobilenet, transformer, explainer

# Transformer
kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=transformer -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > ./logs/mobilenet_fullstack_transformer.log

# Predictor
kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=predictor -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > ./logs/mobilenet_fullstack_predictor.log

# Explainer
kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=explainer -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > ./logs/mobilenet_fullstack_explainer.log

```

---
One-shot Test:

```sh

INFERENCE_NS="ifsvc"
MODEL_NAME="mobilenet-fullstack"  # mobilenet, transformer, explainer
INPUT_PATH="@./input_numpy.json"

# kubectl -n $INFERENCE_NS delete -f mobilenet-fullstack.yaml
kubectl -n $INFERENCE_NS apply -f mobilenet-fullstack.yaml

echo `kubectl -n $INFERENCE_NS wait \
    --for=condition=ready --timeout=120s\
    inferenceservice $MODEL_NAME`
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "
CLUSTER_IP: $CLUSTER_IP
HOSTNAME  : $SERVICE_HOSTNAME"

# PREDICTION
curl -v -H "Host: ${SERVICE_HOSTNAME}" \
  http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict \
  -d $INPUT_PATH > ./logs/output_predict.json

echo "
Predict Log: ./logs/output_predict.json"

# EXPLANATION
# BUG: env_var not working
curl -v \
  --max-time 600 \
  --connect-timeout 600 \
  -H "Host: ${SERVICE_HOSTNAME}" \
  http://104.198.233.27/v1/models/mobilenet-fullstack:explain \
  -d $INPUT_PATH > ./logs/output_explain.json

echo "
Explain Log: ./logs/output_explain.json"

# Transformer
kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=transformer -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > ./logs/mobilenet_fullstack_transformer.log

# Predictor
kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=predictor -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > ./logs/mobilenet_fullstack_predictor.log

# Explainer
kubectl -n $INFERENCE_NS logs "$(kubectl -n $INFERENCE_NS get pods -l model=$MODEL_NAME,component=explainer -o jsonpath='{.items[0].metadata.name}')" -c kfserving-container > ./logs/mobilenet_fullstack_explainer.log

# kubectl -n $INFERENCE_NS delete -f mobilenet-fullstack.yaml
```

```sh
python
```

---

:warning: According to the log of transformer, `dict_keys(['predictions'])` was logged multiple times, for about 4 min, with multiple pods. with `batch_size` in `explainer.yaml` can reduce ETA for explaining.

When `batch_size == 1`, it tooks 3:34 min, 2 `explainer, transformer, predictor` pods each. `dict_keys(['predictions'])` was logged **164 times**.
When `batch_size == 13`, it tooks 4:45 min, 2 `explainer` pods. `dict_keys(['predictions'])` was logged **13 times**.

:warning:
```sh
{ "error": "Failed to process element: 0 key: image_bytes of \'instances\' list. Error: Invalid argument: JSON object: does not have named input: image_bytes" }%   
```

```sh
$ saved_model_cli show --dir . --tag_set serve --signature_def serving_default

The given SavedModel SignatureDef contains the following input(s):
  inputs['input_1'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 224, 224, 3)
      name: serving_default_input_1:0
The given SavedModel SignatureDef contains the following output(s):
  outputs['act_softmax'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 1000)
      name: StatefulPartitionedCall:0
Method name is: tensorflow/serving/predict
```

:warning:
```sh
DWTcja49DWvN1rJuvvGgZl34zAmezGs8NtYEdjWhf/AOpH1/xrPHU1jLcpHbW0omtY3B4YCkccFT0NVNGJOmLn3q3J0rZbEmbJmOQoenUVLBJztqO+6p9aZGTvBpAaQ+YfSoJUzk1Knf6UjfcNUBiXSFTVHcUc+hrTvvu/hWY4+UVEhkoIYUx0psR+apm6VBRUZcUYFSuKZgUAf//Z\" Type: String is not of expected type: float" }
```

---
## Test explainer in `local`

* RUN Predictor
```sh
PREDICTOR_IMAGE="tensorflow/serving:1.14.0"
docker run --rm -it \
    --name predictor \
    --network bridge \
    --mount src="$(pwd)/predictor/mobilenet_saved_model",target=/models/mobilenet-exp,type=bind \
    -e MODEL_NAME=mobilenet-exp \
    -e MODEL_BASE_PATH=/models \
    -p 8500:8500/tcp -p 8501:8501/tcp \
    $PREDICTOR_IMAGE
```

* RUN Explainer
```sh
ALIBIEXPLAINER_IMAGE="docker.io/pydemia/alibiexplainer"
ALIBIEXPLAINER_VERSION="v0.3.2-predict_fn"

docker run --rm -it \
    --name explainer \
    --network bridge \
    --link predictor:predictor \
    --mount src="$(pwd)/explainer",target=/mnt/models,type=bind \
    -p 8081:8081 \
    $ALIBIEXPLAINER_IMAGE:$ALIBIEXPLAINER_VERSION \
    --model_name mobilenet-exp \
    --predictor_host predictor:8501 \
    --http_port 8081 \
    --storage_uri /mnt/models \
    AnchorImages \
    --batch_size 1
```

* Get responses
```sh
# CLUSTER_IP="127.0.0.1:8501"
CLUSTER_IP="127.0.0.1:8081"   # You can call predict on explainer IP.
SERVICE_HOSTNAME="predictor"  # You can call predict on Hostname `explainer` either.

MODEL_NAME="mobilenet-exp"
INPUT_PATH="@./input_numpy.json"

python test_explainer_local.py \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict


# SERVICE_HOSTNAME="explainer"
MODEL_NAME="mobilenet-exp"
INPUT_PATH="@./input_numpy.json"

python test_explainer_local.py \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op explain
```

---

curl -v -H Host:mobnet.default.34.94.79.203.xip.io mobnet.default.34.94.79.203.xip.io http
://34.94.79.203/v1/models/mobnet:explain -d @./input_numpy.json

INFERENCE_NS="default"
MODEL_NAME="mobnet"
CLUSTER_IP="34.94.79.203"
SERVICE_HOSTNAME="mobnet.default.34.94.79.203.xip.io"

curl -v -H "Host:$SERVICE_HOSTNAME mobnet.default.34.94.79.203.xip.io" http://$CLUSTER_IP/v1/models/$MODEL_NAME:explain -d @./input.json


curl -v -H "Host: mobnet.default.34.94.79.203.xip.io" http://34.94.79.203/v1/models/mobnet:explain -d @./input.json

curl -v -H "Host: mobnet.default.34.94.79.203.xip.io" http://34.94.79.203/v1/models/mobnet:explain -d @./input_numpy.json


curl -v -H "Host: mobnet.default.34.94.79.203.xip.io" http://34.94.79.203/v1/models/mobnet:predict -d @./input_numpy.json


curl -v -H "Host: ${SERVICE_HOSTNAME}" http://34.94.79.203/v1/models/mobilenet-fullstack:explain -d @./input_numpy.json > ./output_explain_sm.json



python test_explainer_local.py \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op explain