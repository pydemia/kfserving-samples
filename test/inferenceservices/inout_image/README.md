# Input-Output Test

Mobilenet

```sh
cp -r ../mobilenet ./mobilenet
```

```sh
INFERENCE_NS="ifsvc"
MODEL_NAME="mobilenet-fullstack" 
INPUT_PATH="@./input_numpy.json"
# kubectl -n $INFERENCE_NS apply -f mobilenet/mobilenet-fullstack.yaml

echo `kubectl -n $INFERENCE_NS wait \
    --for=condition=ready --timeout=120s\
    inferenceservice $MODEL_NAME`
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "
CLUSTER_IP: $CLUSTER_IP
HOSTNAME  : $SERVICE_HOSTNAME"
```

```sh
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

```
