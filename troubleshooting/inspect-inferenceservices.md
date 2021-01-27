# Inspect `inferenceservices`

Namespace: `ifsvc`
Name: `sklearn-iris`

```sh
INFERENCE_NS="ifsvc"
MODEL_NAME="sklearn-iris"
```

```sh
kubectl -n ifsvc get inferenceservices sklearn-iris
```

```sh
kubectl -n $INFERENCE_NS wait \
    --for=condition=ready --timeout=90s\
    inferenceservice $MODEL_NAME
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "
CLUSTER_IP: $CLUSTER_IP
HOSTNAME  : $SERVICE_HOSTNAME"

```


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

# RevisionMissing Error
## Storage Initializer fails to download model
# kubectl -n inference-test get revision \
#    $(kubectl -n inference-test get configuration mobilenet-predictor-default \
#     --output jsonpath="{.status.latestCreatedRevisionName}") 
# kubectl -n inference-test get pod -l model=mobilenet

## Inference Service fails to start
# $(kubectl -n inference-test get pod -l model=mobilenet -o jsonpath="{.items..metadata.name}")
# kubectl -n inference-test logs \
#   $(kubectl -n inference-test get pod -l model=mobilenet -o jsonpath="{.items..metadata.name}") \
#   kfserving-container

# kubectl -n inference-test get inferenceservice mobilenet
# kubectl -n inference-test describe inferenceservice mobilenet
# kubectl -n inference-test describe deployment mobilenet
# kubectl -n inference-test get ksvc mobilenet-predictor-default -o yaml
# kubectl -n inference-test get ksvc mobilenet-explainer-default -o yaml
# kubectl -n inference-test get ksvc mobilenet-transformer-default -o yaml
# kubectl -n inference-test get kpa -o yaml
# kubectl -n inference-test get pods -l model=mobilenet
# kubectl -n inference-test describe pods -l model=mobilenet
# kubectl -n inference-test describe deployment mobilenet
# kubectl -n inference-test get revision mobilenet-predictor-default-ttlpz -o yaml
# 
# kubectl -n inference-test get events mobilenet



# kubectl get inferenceservice mobilenet
# kubectl describe inferenceservice mobilenet
# kubectl describe deployment mobilenet
# kubectl get ksvc mobilenet-predictor-default -o yaml
# kubectl get ksvc mobilenet-explainer-default -o yaml
# kubectl get ksvc mobilenet-transformer-default -o yaml
# kubectl get kpa -o yaml
# kubectl get pods -l model=mobilenet
# kubectl describe pods -l model=mobilenet
# kubectl describe deployment mobilenet
# kubectl get revision mobilenet-predictor-default-ttlpz -o yaml
# 
# kubectl get events mobilenet

```bash
kubectl -n knative-serving describe deploy controller 
kubectl get pods --namespace knative-monitoring
kubectl port-forward -n knative-monitoring $(kubectl get pods -n knative-monitoring -l=app=grafana --output=jsonpath="{.items..metadata.name}") 30802
```
