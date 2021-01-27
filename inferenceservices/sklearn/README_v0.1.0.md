# Scikit-learn Inference

Apply the CRD
```sh
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/sklearn.yaml -O
$ kubectl apply -f sklearn.yaml
inferenceservice.serving.kubeflow.org/sklearn-iris created
```

The original source is [here](https://github.com/kubeflow/kfserving/tree/master/docs/samples/sklearn):
```sh
MODEL_NAME=sklearn-iris
INPUT_PATH=@./iris-input.json
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl get inferenceservice sklearn-iris -o jsonpath='{.status.url}' | cut -d "/" -f 3)
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```

kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80 
```sh
MODEL_NAME="sklearn-iris"
INPUT_PATH=./iris-input.json
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.clusterIP}')
kubectl port-forward svc/istio-ingressgateway -n istio-system 80:80 && \
curl -v -H "Content-Type: application/json" http://localhost:80/v1/models/$MODEL_NAME:predict

curl -v http://localhost/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

