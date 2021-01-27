# `InferenceService`: `tensorflow`


* `tensorflow-cpu: flowers-sample`
```bash
INFERENCE_NS=inference-test
kubectl create ns $INFERENCE_NS

# YAML
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/tensorflow/tensorflow-canary.yaml -O
# INPUT SAMPLE
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/tensorflow/input.json -o tf-imagebyte-input.json

MODEL_NAME=flowers-sample
INPUT_PATH=@./tf-imagebyte-input.json

# APPLY
kubectl -n $INFERENCE_NS apply -f tensorflow-canary.yaml

CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)

echo "$CLUSTER_IP, $SERVICE_HOSTNAME"

# PREDICTION
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```
