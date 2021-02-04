# Post-installation after `kfserving`

## Test `inferenceservices`

```bash
kubectl create ns test
kubectl apply -f ./flower-sample.yaml
```

```bash
$ kubectl get inferenceservices -A
NAMESPACE   NAME            URL   READY     PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION   AGE
test        flower-sample         Unknown                                                                 13s

# Knative 0.18.0
NAMESPACE   NAME            URL                                     READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION                     AGE
test        flower-sample   http://flower-sample.test.example.com   True           100                              flower-sample-predictor-default-nvb9j   43s

# Knative 0.20.0
NAMESPACE   NAME            URL                                     READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION                     AGE
test        flower-sample   http://flower-sample.test.example.com   True           100                              flower-sample-predictor-default-00002   63s
```

```bash
INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')
HOSTNAME=$(kubectl get inferenceservice flower-sample -n test -o jsonpath='{.status.url}' | cut -d "/" -f 3)

curl -v POST "http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/flower-sample:predict" \
-H "Host: ${HOSTNAME}" \
-H 'Content-Type: application/json' \
-d '@./flower-input.json'
```

```bash
# API_VERSION=v1alpha2
API_VERSION=v1beta1
kubectl create namespace kfserving-test
kubectl apply -f ./sklearn-iris.yaml -n kfserving-test

kubectl get inferenceservices sklearn-iris -n kfserving-test

INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')

SERVICE_HOSTNAME=$(kubectl get inferenceservice sklearn-iris -n kfserving-test -o jsonpath='{.status.url}' | cut -d "/" -f 3)

curl -fsSL "https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/${API_VERSION}/sklearn/iris-input.json" -o ./test/iris-input.json

curl -v -H "Host: ${SERVICE_HOSTNAME}" "http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/sklearn-iris:predict" -d @./iris-input.json
```