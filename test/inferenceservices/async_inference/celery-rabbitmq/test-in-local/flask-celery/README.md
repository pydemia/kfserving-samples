# API Server: Flask and Celery

## Flask

```sh
docker run --rm -it \
    --name flask-celery \
    -p 5000:5000 \
    --mount src="$(pwd)",target=/tmp/flask-celery,type=bind \
    --workdir /tmp/flask-celery \
    --entrypoint /bin/bash \
    pydemia/celery-dealer:latest

```

```sh
kubectl -n ifsvc run --rm -i --tty tmp --command /bin/bash --image python:3.7
kubectl -n ifsvc-queue run --rm -i --tty tmp --command /bin/bash --image python:3.7

curl https://raw.githubusercontent.com/pydemia/containers/master/kubernetes/apps/kfserving/examples/mobilenet/input_numpy.json -O

curl -v -H "Host: mobilenet-prd-predictor-default.ifsvc.svc.cluster.local"  http://cluster-local-gateway.istio-system/v1/models/mobilenet-prd:predict -d @./input_numpy.json

```

Tracking gateways:
```sh
$ kubectl -n ifsvc get vs mobilenet-prd

NAME            GATEWAYS                                                                          HOSTS                                                                               AGE
mobilenet-prd   [knative-ingress-gateway.knative-serving knative-serving/cluster-local-gateway]   [mobilenet-prd.ifsvc.104.198.233.27.xip.io mobilenet-prd.ifsvc.svc.cluster.local]   32h

$ kubectl -n ifsvc get vs mobilenet-prd -o yaml

apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"serving.kubeflow.org/v1alpha2","kind":"InferenceService","metadata":{"annotations":{},"controller-tools.k8s.io":"1.0","name":"mobilenet-prd","namespace":"ifsvc"},"spec":{"default":{"predictor":{"serviceAccountName":"yjkim-private-deployer-s3","tensorflow":{"storageUri":"s3://yjkim-models/kfserving/mobilenet/predictor/mobilenet_saved_model"}}}}}
  creationTimestamp: "2020-06-01T07:33:03Z"
  generation: 1
  name: mobilenet-prd
  namespace: ifsvc
  ownerReferences:
  - apiVersion: serving.kubeflow.org/v1alpha2
    blockOwnerDeletion: true
    controller: true
    kind: InferenceService
    name: mobilenet-prd
    uid: 674e2caa-eb32-4ee3-942a-cd440bd1941a
  resourceVersion: "2981951"
  selfLink: /apis/networking.istio.io/v1alpha3/namespaces/ifsvc/virtualservices/mobilenet-prd
  uid: bccd78b0-c3c5-4cac-89e2-07ab72deae58
spec:
  gateways:
  - knative-ingress-gateway.knative-serving
  - knative-serving/cluster-local-gateway
  hosts:
  - mobilenet-prd.ifsvc.104.198.233.27.xip.io
  - mobilenet-prd.ifsvc.svc.cluster.local
  http:
  - match:
    - authority:
        regex: ^mobilenet-prd\.ifsvc\.104\.198\.233\.27\.xip\.io(?::\d{1,5})?$
      gateways:
      - knative-ingress-gateway.knative-serving
      uri:
        prefix: /v1/models/mobilenet-prd:predict
    - authority:
        regex: ^mobilenet-prd\.ifsvc(\.svc(\.cluster\.local)?)?(?::\d{1,5})?$
      gateways:
      - knative-serving/cluster-local-gateway
      uri:
        prefix: /v1/models/mobilenet-prd:predict
    retries:
      attempts: 3
      perTryTimeout: 600s
    route:
    - destination:
        host: cluster-local-gateway.istio-system.svc.cluster.local
        port:
          number: 80
      headers:
        request:
          set:
            Host: mobilenet-prd-predictor-default.ifsvc.svc.cluster.local
      weight: 100

$ kubectl -n istio-system get svc cluster-local-gateway -o yaml

apiVersion: v1
kind: Service
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"app":"cluster-local-gateway","chart":"gateways","heritage":"Helm","istio":"cluster-local-gateway","release":"RELEASE-NAME"},"name":"cluster-local-gateway","namespace":"istio-system"},"spec":{"ports":[{"name":"status-port","port":15020},{"name":"http2","port":80},{"name":"https","port":443}],"selector":{"app":"cluster-local-gateway","istio":"cluster-local-gateway","release":"RELEASE-NAME"},"type":"ClusterIP"}}
  creationTimestamp: "2020-05-26T15:31:18Z"
  labels:
    app: cluster-local-gateway
    chart: gateways
    heritage: Helm
    istio: cluster-local-gateway
    release: RELEASE-NAME
  name: cluster-local-gateway
  namespace: istio-system
  resourceVersion: "1983"
  selfLink: /api/v1/namespaces/istio-system/services/cluster-local-gateway
  uid: c9547ab9-a780-49f6-8999-48184c00bcef
spec:
  clusterIP: 10.122.11.245
  ports:
  - name: status-port
    port: 15020
    protocol: TCP
    targetPort: 15020
  - name: http2
    port: 80
    protocol: TCP
    targetPort: 80
  - name: https
    port: 443
    protocol: TCP
    targetPort: 443
  selector:
    app: cluster-local-gateway
    istio: cluster-local-gateway
    release: RELEASE-NAME
  sessionAffinity: None
  type: ClusterIP
status:
  loadBalancer: {}

$ kubectl -n knative-serving get gw cluster-local-gateway -o yaml

apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"networking.istio.io/v1alpha3","kind":"Gateway","metadata":{"annotations":{},"labels":{"networking.knative.dev/ingress-provider":"istio","serving.knative.dev/release":"v0.14.0"},"name":"cluster-local-gateway","namespace":"knative-serving"},"spec":{"selector":{"istio":"cluster-local-gateway"},"servers":[{"hosts":["*"],"port":{"name":"http","number":80,"protocol":"HTTP"}}]}}
  creationTimestamp: "2020-05-26T15:33:59Z"
  generation: 1
  labels:
    networking.knative.dev/ingress-provider: istio
    serving.knative.dev/release: v0.14.0
  name: cluster-local-gateway
  namespace: knative-serving
  resourceVersion: "3104"
  selfLink: /apis/networking.istio.io/v1alpha3/namespaces/knative-serving/gateways/cluster-local-gateway
  uid: 6d11eca5-2a83-45e9-aae0-b55d603a8554
spec:
  selector:
    istio: cluster-local-gateway
  servers:
  - hosts:
    - '*'
    port:
      name: http
      number: 80
      protocol: HTTP

$ kubectl -n knative-serving get gw knative-ingress-gateway -o yaml

apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"networking.istio.io/v1alpha3","kind":"Gateway","metadata":{"annotations":{},"labels":{"networking.knative.dev/ingress-provider":"istio","serving.knative.dev/release":"v0.14.0"},"name":"knative-ingress-gateway","namespace":"knative-serving"},"spec":{"selector":{"istio":"ingressgateway"},"servers":[{"hosts":["*"],"port":{"name":"http","number":80,"protocol":"HTTP"}}]}}
  creationTimestamp: "2020-05-26T15:33:59Z"
  generation: 1
  labels:
    networking.knative.dev/ingress-provider: istio
    serving.knative.dev/release: v0.14.0
  name: knative-ingress-gateway
  namespace: knative-serving
  resourceVersion: "3099"
  selfLink: /apis/networking.istio.io/v1alpha3/namespaces/knative-serving/gateways/knative-ingress-gateway
  uid: 19ed7cf7-a8c3-44f4-a1e7-91d96f5af63f
spec:
  selector:
    istio: ingressgateway
  servers:
  - hosts:
    - '*'
    port:
      name: http
      number: 80
      protocol: HTTP
```