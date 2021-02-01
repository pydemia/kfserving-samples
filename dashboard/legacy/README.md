# Expose Monitoring
`Istio == 1.4`
<https://archive.istio.io/v1.4/docs/tasks/observability/gateways/>


## Installation


### Install `grafana` on Istio

```sh
$ istioctl manifest apply --set values.grafana.enabled=true
```

```sh
istioctl manifest apply \
    --set values.prometheus.enabled=true \
    --set values.grafana.enabled=true \
    --set values.kiali.enabled=true \
    --set values.tracing.enabled=true
```

```sh
$ kubectl -n istio-system get svc prometheus
$ kubectl -n istio-system get svc grafana
```

```
$ kubectl -n istio-system port-forward $(kubectl -n istio-system get pod -l app=grafana -o jsonpath='{.items[0].metadata.name}') 3000:3000 &
$ istioctl dashboard prometheus
$ istioctl dashboard grafana
```

#### Set `grafana`


##### Create a new organization and an API Token

```sh
$ CLUSTER_IP=35.223.126.238
$ CLUSTER_GRAFANA=35.223.126.238/knative/grafana
$ CLUSTER_GRAFANA=35.193.25.78:30802
$ curl http://$CLUSTER_GRAFANA/api/org
{"id":1,"name":"Main Org.","address":{"address1":"","address2":"","city":"","zipCode":"","state":"","country":""}}
```

```sh
# Create an org
# curl -X POST -H "Content-Type: application/json" -d '{"name":"apiorg"}' http://admin:admin@localhost:3000/api/orgs
$ curl -X POST -H "Content-Type: application/json" -d '{"name":"airuntime"}' http://admin:admin@$CLUSTER_GRAFANA/api/orgs
{"message":"Organization created","orgId":2}
$ curl -X POST -H "Content-Type: application/json" -d '{"name":"pydemia"}' http://admin:admin@$CLUSTER_GRAFANA/api/orgs
{"message":"Organization created","orgId":3}

$ curl -X DELETE -H "Content-Type: application/json" http://admin:admin@$CLUSTER_GRAFANA/api/orgs/2

# Create a new user. Only works with Basic Authentication (username and password).
$ curl -X POST -H "Content-Type: application/json" http://admin:admin@$CLUSTER_GRAFANA/api/admin/users -d \
'{
  "name":"airuntime",
  "email":"silencez@sk.com",
  "login":"airuntime",
  "password":"airuntime",
  "OrgId": 2
}'
{"id":2,"message":"User created"}

# (Optional) Add your admin user to the org
$ curl -X POST -H "Content-Type: application/json" -d '{"loginOrEmail":"airuntime", "role": "Admin"}' http://admin:admin@$CLUSTER_GRAFANA/api/orgs/2/users
{"message":"User added to organization"}
$ curl -X POST -H "Content-Type: application/json" -d '{"loginOrEmail":"admin", "role": "Admin"}' http://admin:admin@$CLUSTER_GRAFANA/api/orgs/2/users
{"message":"User is already member of this organization"}

# Switch the org context for the Admin user to the new org
$ curl -X POST http://airuntime:airuntime@$CLUSTER_GRAFANA/api/user/using/2
{"message":"Active organization changed"}
# $ curl -X POST http://admin:admin@$CLUSTER_GRAFANA/api/user/using/1
# {"message":"Active organization changed"}

# Create the API token
$ curl -X POST -H "Content-Type: application/json" -d '{"name":"airuntime-apikey", "role": "Admin"}' http://airuntime:airuntime@$CLUSTER_GRAFANA/api/auth/keys
{"name":"airuntime-apikey","key":"eyJrIjoiTllzSmowaUZuIjoiYWlydW50aW1lLWFwaWtleSIsImMT1pmbWJVY2JQNUdoYUlzRG16NnpZSEciLCJlkIjoyfQ=="}
# $ curl -X POST -H "Content-Type: application/json" -d '{"name":"pydemia-apikey", "role": "Admin"}' http://admin:admin@$CLUSTER_GRAFANA/api/auth/keys
# {"name":"pydemia-apikey","key":"eyJrIjoiblU0ZXdLekliblZyN0lueG5vdTN5NzEwZTRDazZOM1ciLCJuIjoicHlkZW1pYS1hcGlrZXkiLCJpZCI6Mn0="}

# Create a dashboard
$ curl -X POST --insecure -H "Authorization: Bearer eyJrIjoiT0NTQnQ5bjIwRTFzUUhFcjNWU1U1YnpaOFhOdlNUQ20iLCJuIjoiYWlydW50aW1lLWFwaWtleSIsImlkIjoyfQ==" -H "Content-Type: application/json" -d '{
  "dashboard": {
    "id": null,
    "uid": "airuntime",
    "annotations": {
          "list":[]
      },
    "tags": [ "templated" ],
    "templating": {
        "list": []
    },
    "editable": true,
    "gnetId": null,
    "title": "Sample Dashboard-airuntime",
    "iteration": 1529322539820,
    "links":[],
    "panels": [{}],
    "rows": [
      {
      }
    ],
    "__inputs": [],
    "__requires": [],  
    "timezone": "browser",
    "schemaVersion": 6,
    "style": "dark",
    "version": 0
  },
  "inputs": [],
  "overwrite": false
}' http://$CLUSTER_GRAFANA/api/dashboards/db
{"id":15,"slug":"sample-dashboard-pydemia","status":"success","uid":"airuntime","url":"/knative/grafana/d/airuntime/sample-dashboard-pydemia","version":1}

# $ curl -X POST --insecure -H "Authorization: Bearer eyJrIjoiblU0ZXdLekliblZyN0lueG5vdTN5NzEwZTRDazZOM1ciLCJuIjoicHlkZW1pYS1hcGlrZXkiLCJpZCI6Mn0=" -H "Content-Type: application/json" -d '{
#   "dashboard": {
#     "id": null,
#     "uid": "pydemia",
#     "annotations": {
#           "list":[]
#       },
#     "tags": [ "templated" ],
#     "templating": {
#         "list": []
#     },
#     "editable": true,
#     "gnetId": null,
#     "title": "Sample Dashboard-pydemia",
#     "iteration": 1529322539820,
#     "links":[],
#     "panels": [{}],
#     "rows": [
#       {
#       }
#     ],
#     "__inputs": [],
#     "__requires": [],  
#     "timezone": "browser",
#     "schemaVersion": 6,
#     "style": "dark",
#     "version": 0
#   },
#   "inputs": [],
#   "overwrite": false
# }' http://$CLUSTER_GRAFANA/api/dashboards/db

# {"id":15,"slug":"sample-dashboard-pydemia","status":"success","uid":"uid","url":"/d/uid/sample-dashboard-pydemia","version":1}

# Get the dashboard
$ curl -X GET -H "Accept: application/json;Content-Type: application/json;Authorization: Bearer eyJrIjoiblU0ZXdLekliblZyN0lueG5vdTN5NzEwZTRDazZOM1ciLCJuIjoicHlkZW1pYS1hcGlrZXkiLCJpZCI6Mn0=" http://admin:admin@$CLUSTER_GRAFANA/api/dashboards/uid/pydemia

{"meta":{"type":"db","canSave":true,"canEdit":true,"canAdmin":true,"canStar":true,"slug":"sample-dashboard-pydemia","url":"/d/pydemia/sample-dashboard-pydemia","expires":"0001-01-01T00:00:00Z","created":"2020-05-19T18:25:03Z","updated":"2020-05-19T18:25:03Z","updatedBy":"Anonymous","createdBy":"Anonymous","version":1,"hasAcl":false,"isFolder":false,"folderId":0,"folderTitle":"General","folderUrl":"","provisioned":false,"provisionedExternalId":""},"dashboard":{"__inputs":[],"__requires":[],"annotations":{"list":[]},"editable":true,"gnetId":null,"id":16,"iteration":1529322539820,"links":[],"panels":[{}],"rows":[{}],"schemaVersion":6,"style":"dark","tags":["templated"],"templating":{"list":[]},"timezone":"browser","title":"Sample Dashboard-pydemia","uid":"pydemia","version":1}}

$ curl -X GET -H "Accept: application/json;Content-Type: application/json;Authorization: Bearer eyJrIjoiblU0ZXdLekliblZyN0lueG5vdTN5NzEwZTRDazZOM1ciLCJuIjoicHlkZW1pYS1hcGlrZXkiLCJpZCI6Mn0=" http://admin:admin@$CLUSTER_GRAFANA/api/dashboards/home

# Delete the dashboard
$ curl -X DELETE -H "Content-Type: application/json" -d '{"name":"airuntime-apikey", "role": "Admin"}' http://airuntime:airuntime@$CLUSTER_GRAFANA/api/dashboards/db/sample-dashboard-pydemia 
$ curl -X DELETE -H "Content-Type: application/json" -d '{"name":"pydemia-apikey", "role": "Admin"}' http://admin:admin@$CLUSTER_GRAFANA/api/dashboards/db/sample-dashboard-pydemia 
{"message":"Dashboard Sample Dashboard-pydemia deleted","title":"Sample Dashboard-pydemia"}
```

kubectl -n knative-serving describe deploy controller 
kubectl get pods --namespace knative-monitoring
kubectl port-forward -n knative-monitoring $(kubectl get pods -n knative-monitoring -l=app=grafana --output=jsonpath="{.items..metadata.name}") 30802

`grafana-custom-config`
```yaml
apiVersion: v1
kind: ConfigMap
name: grafana-custom-config
  namespace: knative-monitoring
data:
  custom.ini: |
    # You can customize Grafana via changing context of this field.
    [auth.anonymous]
    # enable anonymous access
    enabled = true
    [server]
    protocol = http
    domain = 35.223.25.173
    http_port = 3000
    root_url = %(protocol)s://%(domain)s:%(http_port)s/grafana
    serve_from_sub_path = true
    [security]
    allow_embedding = true
```



### Install `kiali` on Istio

```sh
$ istioctl manifest apply --set values.kiali.enabled=true \
  --set values.grafana.enabled=true \
  --set "values.kiali.dashboard.grafanaURL=http://grafana:3000"
```

Generating a service graph
```sh
$ kubectl -n istio-system get svc kiali
```


* `bash`
```bash
# Username & Passphrase
KIALI_USERNAME=$(read -p 'Kiali Username: ' uval && echo -n $uval | base64) && \
  KIALI_PASSPHRASE=$(read -sp 'Kiali Passphrase: ' pval && echo -n $pval | base64)
```

* `zsh`
```zsh
# Username & Passphrase
KIALI_USERNAME=$(read '?Kiali Username: ' uval && echo -n $uval | base64) && \
  KIALI_PASSPHRASE=$(read -s "?Kiali Passphrase: " pval && echo -n $pval | base64)
```

Then, create a secret:
```sh
# $ NAMESPACE=istio-system && \
#   kubectl create namespace $NAMESPACE

$ NAMESPACE=istio-system && \
  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: kiali
  namespace: $NAMESPACE
  labels:
    app: kiali
type: Opaque
data:
  username: $KIALI_USERNAME
  passphrase: $KIALI_PASSPHRASE
EOF

```
secret/kiali created
```

Restart Kiali

```sh
kubectl -n istio-system rollout restart deployment kiali
```

--- 

# Exposing Dashboards

## Istio, HTTP

* `grafana`: --set values.grafana.enabled=true
* `kiali`: --set values.kiali.enabled=true
* `prometheus`: --set values.prometheus.enabled=true
* `tracing`: --set values.tracing.enabled=true


```bash
# 1.7
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/grafana.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/jaeger.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/kiali.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/prometheus.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/extras/zipkin.yaml

# 1.8
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/grafana.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/jaeger.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/kiali.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/prometheus.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.8/samples/addons/extras/zipkin.yaml

```

```sh
# cd prometheus-and-grafana

kubectl apply -f expose-istio-grafana-http.yaml
kubectl apply -f expose-istio-kiali-http.yaml
kubectl apply -f expose-istio-prometheus-http.yaml
kubectl apply -f expose-istio-tracing-http.yaml
```

* `grafana`: http://$CLUSTER_IP:15031
* `kiali`: http://$CLUSTER_IP:15029
* `prometheus`: http://$CLUSTER_IP:15030
* `tracing`: http://$CLUSTER_IP:15032


expose-istio-grafana-http-url.yaml  expose-istio-prometheus-http.yaml  grafana-dashboard-import.json                                     nginx-ingress-controller.yaml
expose-istio-grafana-http.yaml      expose-istio-tracing-http.yaml     knative-prom-graf.yaml                                            README.md
expose-istio-kiali-http.yaml        expose-monitoring.yaml  


### `grafana`

```yaml
$ cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: grafana-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 15031
      name: http-grafana
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: grafana-vs
  namespace: istio-system
spec:
  hosts:
  - "*"
  gateways:
  - grafana-gateway
  http:
  - match:
    - port: 15031
    route:
    - destination:
        host: grafana
        port:
          number: 3000
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: grafana
  namespace: istio-system
spec:
  host: grafana
  trafficPolicy:
    tls:
      mode: DISABLE
---
EOF
```

### `kiali`

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: kiali-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 15029
      name: http-kiali
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: kiali-vs
  namespace: istio-system
spec:
  hosts:
  - "*"
  gateways:
  - kiali-gateway
  http:
  - match:
    - port: 15029
    route:
    - destination:
        host: kiali
        port:
          number: 20001
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: kiali
  namespace: istio-system
spec:
  host: kiali
  trafficPolicy:
    tls:
      mode: DISABLE
---
EOF
```

### `prometheus`

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: prometheus-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 15030
      name: http-prom
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: prometheus-vs
  namespace: istio-system
spec:
  hosts:
  - "*"
  gateways:
  - prometheus-gateway
  http:
  - match:
    - port: 15030
    route:
    - destination:
        host: prometheus
        port:
          number: 9090
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: prometheus
  namespace: istio-system
spec:
  host: prometheus
  trafficPolicy:
    tls:
      mode: DISABLE
---
EOF
```

### tracing

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: tracing-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 15032
      name: http-tracing
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: tracing-vs
  namespace: istio-system
spec:
  hosts:
  - "*"
  gateways:
  - tracing-gateway
  http:
  - match:
    - port: 15032
    route:
    - destination:
        host: tracing
        port:
          number: 80
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: tracing
  namespace: istio-system
spec:
  host: tracing
  trafficPolicy:
    tls:
      mode: DISABLE
---
EOF
```

---

# Expose Knative-monitoring

<https://grafana.com/docs/grafana/latest/installation/configuration/>

## Grafana

```sh
data:
  custom.ini: |
    # You can customize Grafana via changing context of this field.
    [auth.anonymous]
    # enable anonymous access
    enabled = true
    [server]
    protocol = http
    domain = localhost
    http_port = 3000
    root_url = %(protocol)s://%(domain)s:%(http_port)s/knative/grafana/
    serve_from_sub_path = true
```


```sh
$ kubectl -n knative-monitoring patch configmap/grafana-custom-config \
    --type merge -p "$(cat knative-components/patch-knative-monitoring-grafana-custom-config-ini.yaml)"
configmap/grafana-custom-config patched

$ kubectl -n knative-monitoring rollout restart deployment grafana
deployment.extensions/grafana restarted
```

```sh
$ kubectl apply -f knative-components/expose-knative-monitoring.yaml

$ kubectl apply -f knative-components/expose-knative-zipkin-http.yaml
```
---


목록:
| namespace          | service              | address                                  |
|--------------------|----------------------|------------------------------------------|
| istio-system       | kiali                | <http://kfs.pydemia.org:15029>           |
| istio-system       | prometheus           | <http://kfs.pydemia.org:15030>           |
| istio-system       | grafana              | <http://kfs.pydemia.org:15031>           |
| istio-system       | tracing              | <http://kfs.pydemia.org:15032>           |
| istio-system       | zipkin               | <http://kfs.pydemia.org:15033>           |
| knative-monitoring | grafana              | <http://kfs.pydemia.org/knative/grafana> |
| knative-monitoring | prometheus-system-np | <http://kfs.pydemia.org:15034>           |
