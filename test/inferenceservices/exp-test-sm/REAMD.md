
## Test explainer in `local`

```bash
docker network create -d bridge test-kfs
```

* RUN Predictor
```sh
NETWORK_NM="test-kfs"  # bridge
PREDICTOR_IMAGE="tensorflow/serving:1.14.0"
docker run --rm -it \
    --name predictor \
    --network $NETWORK_NM \
    --mount src="$(pwd)/predictor/mobilenet_saved_model",target=/models/mobilenet-exp,type=bind \
    -e MODEL_NAME=mobilenet-exp \
    -e MODEL_BASE_PATH=/models \
    -p 8500:8500/tcp \
    -p 8501:8501/tcp \
    $PREDICTOR_IMAGE
```

* RUN Explainer
```sh
NETWORK_NM="test-kfs"  # bridge
ALIBIEXPLAINER_IMAGE="docker.io/pydemia/alibiexplainer"
ALIBIEXPLAINER_VERSION="v0.3.2-predict_fn"


docker run --rm -it \
    --name explainer \
    --network $NETWORK_NM \
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

python test_inference.py \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict


SERVICE_HOSTNAME="explainer"
MODEL_NAME="mobilenet-exp"
INPUT_PATH="@./input_numpy.json"

python test_inference.py \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op explain
```