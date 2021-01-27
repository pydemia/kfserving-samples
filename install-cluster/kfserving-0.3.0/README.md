# KFServing

## Installation

`KFServing: v0.3.0`

* Prerequisite:
  * `Istio: v1.1.6+`(`v1.3.1+` for `dex`) -> 1.4.1
  * `Cert Manager: v1.12.0+`
  * `Knative Serving: v0.11.1+`

---
First, Unless your're the owner of the cluster,
```sh
kubectl create clusterrolebinding cluster-admin-binding \
    --clusterrole=cluster-admin \
    --user=$(gcloud config get-value core/account)
```
---

### Install `Cert-Manager`

```sh
curl -sL https://github.com/jetstack/cert-manager/releases/download/v0.15.0/cert-manager.yaml -O && kubectl apply --validate=false -f cert-manager.yaml
```


### Install `Istio`

* [Install `Istio` for `Knative`](../istio/install_istio_for_knative_v0.14.md)

### Install `Knative`

* [Install `Knative`](../knative/README.md)

`Knative >= v0.14.0`
```sh
cd ../knative
./install-knative-v0.14-istio-no-tls.sh
# kubectl create cm config-istio \
#   --from-file ../istio/config-istio-knative-v0.14.0.yaml
```
:no_entry: `prometheus` response timeout.
> ```sh
> Error from server (Timeout): error when creating "monitoring-metrics-prometheus.yaml": Timeout: request did not complete within requested timeout 30s
> ```

```sh
# 9. Monitor all Knative components are running:
$ kubectl get pods -n knative-serving && \
    kubectl get pods -n knative-eventing && \
    kubectl get pods -n knative-monitoring
```

---
## Install KFServing

```sh
# TAG=0.2.2 && \
# wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
#     -O "kfserving-${TAG}.yaml"
# kubectl apply -f "kfserving-${TAG}.yaml"

TAG=v0.3.0 && \
wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml \
    -O "kfserving-${TAG}.yaml"
kubectl apply -f "kfserving-${TAG}.yaml"

# Setting for KFServing pod mutator
# Set Env-var `ENABLE_WEBHOOK_NAMESPACE_SELECTOR` to the Pods have
# `labels: serving.kubeflow.org/inferenceservice: enabled`
## For Kubernetes >= 1.15
kubectl patch \
    mutatingwebhookconfiguration inferenceservice.serving.kubeflow.org \
    --patch '{"webhooks":[{"name": "inferenceservice.kfserving-webhook-server.pod-mutator","objectSelector":{"matchExpressions":[{"key":"serving.kubeflow.org/inferenceservice", "operator": "Exists"}]}}]}'
```

> :no_entry: **Caution with KFServing Standalone**:
>
> KFServing을 독립형으로 설치했을 경우에는 KFServing 컨트롤러는 kfserving-system 네임스페이스에 배포됩니다.
> KFServing은 `pod mutator`와 `mutating admission webhooks` 을 사용하여 KFServing의 스토리지 이니셜라이저(`storage initializer`) 컴포넌트를 주입합니다. 기본적으론 네임스페이스에 `control-plane` 레이블이 지정되어 있지 않으면, 해당 네임스페이스의 포드들은 `pod mutator`를 통과합니다. 그렇기 때문에 KFServing의 `pod mutator`의 `webhook`이 필요 없는 포드가 실행될때 문제가 발생할 수 있습니다.
> 쿠버네티스 1.14 사용자의 경우 `serving.kubeflow.org/inferenceservice: enabled` 레이블이 추가된 네임스페이스의 포드에 `ENABLE_WEBHOOK_NAMESPACE_SELECTOR` 환경변수를 추가하여, `KFServing pod mutator`를 통과하도록 하는게 좋습니다.
>
> **Ref 1**: <https://github.com/kubeflow/kfserving#standalone-kfserving-installation>
> **Ref 2**: <https://www.kangwoo.kr/2020/04/11/kubeflow-kfserving-%EC%84%A4%EC%B9%98>

```yaml
# # Fro kube 1.14
# env:
# - name: ENABLE_WEBHOOK_NAMESPACE_SELECTOR
#   value: enabled
```

---

* KFServing를 서비스하는 Ingress Gateway 확인

```sh
# $ kubectl -n knative-serving get cm config-istio \
#   -o jsonpath="{.data['gateway\.knative-ingress-gateway']}"
$ kubectl -n knative-serving get cm config-istio \
  -o jsonpath="{.data['gateway\.knative-serving\.knative-ingress-gateway']}"
istio-ingressgateway.istio-system.svc.cluster.local
```

If vanilla:

```sh
kubectl -n knative-serving patch configmap/config-istio \
  --type merge \
  --patch \
'{"data": {"gateway.knative-serving.knative-ingress-gateway": "istio-ingressgateway.istio-system.svc.cluster.local","local-gateway.knative-serving.cluster-local-gateway": "cluster-local-gateway.istio-system.svc.cluster.local","local-gateway.mesh": "mesh"}}'
```

:bell::speech_balloon:**Note**: The configuration format should be `gateway.{{gateway_namespace}}.{{gateway_name}}: "{{ingress_name}}.{{ingress_namespace}}.svc.cluster.local"`.
The `{{gateway_namespace}}` is optional.
when it is omitted, the system will search for the gateway in the serving system namespace `knative-serving`.
gateway.knative-serving.knative-ingress-gateway: "istio-ingressgateway.istio-system.svc.cluster.local".

* It can be shown in `ConfigMap` of `InferenceService`. It contains:
  * data
    * ingress: **Ingress** allocation info
    * logger: **Logging Pods** config
    * predictor: **Inference Container Image** info

```sh
$ gateway.knative-serving.knative-ingress-gateway: "istio-ingressgateway.istio-system.svc.cluster.local"

$ kubectl -n kfserving-system get cm inferenceservice-config -o jsonpath="{.data.ingress}"
{
    "ingressGateway" : "knative-ingress-gateway.knative-serving",
    "ingressService" : "istio-ingressgateway.istio-system.svc.cluster.local"
}
```
:warning: **THIS IS _STRING_, YOU CANNOT GET `jsonpath="{.data.ingress.ingressService}"`**, only `"{.data.ingress}"`.  
*`|-` in `YAML`: multi-line string.

~~`kubectl -n kfserving-system get cm inferenceservice-config -o jsonpath="{.data.ingress}"| sed 's/^[{} \t]*//g' | awk '/"ingressService"/ {print}'`~~

---

* Get `Ingress` for `KFServing` info:
```sh
# kubectl -n istio-system get service istio-ingressgateway
$ kubectl -n knative-serving get cm config-istio \
    -o jsonpath="{.data['gateway\.knative-serving\.knative-ingress-gateway']}" | cut -d '.' -f1,2 | IFS=. read ING_NM ING_NS && \
    kubectl -n $ING_NS get service $ING_NM

$ kubectl -n kfserving-system get cm inferenceservice-config \
    -o jsonpath="{.data.ingress}"| sed 's/^[{} \t]*//g' | awk -F'"' '/"ingressService"/ {print $4}' | cut -d '.' -f1,2 | IFS=. read ING_NM ING_NS && \
    kubectl -n $ING_NS get service $ING_NM
```

---

## Create an `inferenceservice`

```bash
# kubectl apply -f examples/sklearn/sklearn.yaml
$ kubectl create nm inference-test
$ curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/sklearn.yaml -O && \
  kubectl apply -f sklearn.yaml

inferenceservice.serving.kubeflow.org/sklearn-iris created
```

####:speech_balloon::bell:KFServing in Kubeflow Installation (from [github/kubeflow](https://github.com/kubeflow/kfserving/blob/master/README.md#kfserving-in-kubeflow-installation))
`KFServing` is installed by default as part of `Kubeflow` installation using `Kubeflow` manifests and `KFServing` controller is deployed in kubeflow namespace.

Since Kubeflow Kubernetes minimal requirement is **`1.14` <font color="red">which does not support `object selector`</font>**, `ENABLE_WEBHOOK_NAMESPACE_SELECTOR` is enabled in Kubeflow installation by default. 

If you are using Kubeflow dashboard or profile controller to create user namespaces, **labels are automatically added to enable KFServing to deploy models.**

If you are creating namespaces manually using Kubernetes apis directly,
<font color="red">you will need to add label **`serving.kubeflow.org/inferenceservice: enabled`**</font> **to allow deploying** `KFServing InferenceService` **in the given namespaces**, and do ensure you do not deploy `InferenceService` in kubeflow namespace which is labelled as `control-panel`.

```sh
kubectl create ns inference-test
kubectl label ns inference-test serving.kubeflow.org/inferenceservice=enabled

kubectl apply -f - <<EOF
apiVersion: "serving.kubeflow.org/v1alpha2"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
  namespace: "inference-test"
  labels:
    serving.kubeflow.org/inferenceservice: enabled
spec:
  default:
    predictor:
      sklearn:
        storageUri: "gs://kfserving-samples/models/sklearn/iris"
EOF
```

:white_check_mark: **SUCCESS!**
```ascii
namespace/inference-test created
inferenceservice.serving.kubeflow.org/sklearn-iris created
```


> :no_entry: **Error Case:**
> ```ascii
> Error from server (InternalError): error when creating "sklearn.yaml": Internal error occurred: failed calling webhook "inferenceservice.kfserving-webhook-server.defaulter": Post https://kfserving-webhook-server-service.kfserving-system.svc:443/mutate-inferenceservices?timeout=30s: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
> ```
> 
> :white_check_mark:**Troubleshooting:**
> 
> <https://cloud.google.com/run/docs/gke/troubleshooting#deployment_to_private_cluster_failure_failed_calling_webhook_error>
> 
> ```sh
> $ kubectl get po -n kfserving-system
> NAME                             READY   STATUS    RESTARTS   AGE
> kfserving-controller-manager-0   2/2     Running   1          27m
> 
> 
> # If it is, more often than not, it is caused by a stale webhook, since webhooks are immutable.
> # Even if the KFServing controller is not running,
> # you might have stale webhooks from last deployment causing other issues.
> # Best is to delete them, and test again
> $ kubectl -n kfserving-system \
>       delete mutatingwebhookconfigurations inferenceservice.serving.kubeflow.org && \
>     kubectl delete validatingwebhookconfigurations inferenceservice.serving.kubeflow.org && \
>     kubectl delete po kfserving-controller-manager-0
> mutatingwebhookconfiguration.admissionregistration.k8s.io "inferenceservice.serving.kubeflow.org" deleted
> validatingwebhookconfiguration.admissionregistration.k8s.io "inferenceservice.serving.kubeflow.> org" deleted
> pod "kfserving-controller-manager-0" deleted
> ```

## Get a prediction

Samples are [here](https://github.com/kubeflow/kfserving/tree/master/docs/samples)

* `scikit-learn: iris`
```bash
INFERENCE_NS=inference-test
INFERENCE_NS=infer
kubectl create ns $INFERENCE_NS

kubectl label ns $INFERENCE_NS serving.kubeflow.org/inferenceservice=enabled

# YAML
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/sklearn.yaml -O
# INPUT SAMPLE
curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/iris-input.json -O

MODEL_NAME=sklearn-iris
INPUT_PATH=@./iris-input.json

# APPLY
kubectl -n $INFERENCE_NS apply -f sklearn.yaml

CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)

echo "$CLUSTER_IP, $SERVICE_HOSTNAME"

# PREDICTION
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```

* `tensorflow-cpu: flowers-sample`
```bash
INFERENCE_NS=inference-test
kubectl create ns $INFERENCE_NS

kubectl label ns $INFERENCE_NS serving.kubeflow.org/inferenceservice=enabled

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

```sh
kubectl label ns default serving.kubeflow.org/inferenceservice=enabled
kubectl label ns infer serving.kubeflow.org/inferenceservice=enabled
```

---

### Custom Image & Input

---

### Volume

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: kfserving-models-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

---
