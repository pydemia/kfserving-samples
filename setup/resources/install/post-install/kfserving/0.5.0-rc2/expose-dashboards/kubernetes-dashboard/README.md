# Kubernetes Dashboard

## Installation

### Quickstart Installation

[Available arguments](https://github.com/kubernetes/dashboard/blob/master/docs/common/dashboard-arguments.md)

* Default values
```bash
...
  ports:
    - containerPort: 8443
      protocol: TCP
  args:
    - --auto-generate-certificates
    - --namespace=kubernetes-dashboard
    # Uncomment the following line to manually specify Kubernetes API server Host
    # If not specified, Dashboard will attempt to auto discover the API server and connect
    # to it. Uncomment only if the default does not work.
    # - --apiserver-host=http://my-address:port
  volumeMounts:
    - name: kubernetes-dashboard-certs
      mountPath: /certs
      # Create on-disk volume to store exec logs
    - mountPath: /tmp
      name: tmp-volume
  livenessProbe:
    httpGet:
      scheme: HTTPS
      path: /
      port: 8443
    initialDelaySeconds: 30
    timeoutSeconds: 30
  securityContext:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    runAsUser: 1001
    runAsGroup: 2001
volumes:
- name: kubernetes-dashboard-certs
  secret:
    secretName: kubernetes-dashboard-certs
- name: tmp-volume
  emptyDir: {}
serviceAccountName: kubernetes-dashboard
...
```

* Modified values

```bash
# --authentication-mode=basic
  args:
    - --insecure-port=9090
    - --auto-generate-certificates=false
    - --authentication-mode=basic
    - --namespace=kubernetes-dashboard
  volumeMounts:
    - name: kubernetes-dashboard-certs
      mountPath: /certs
volumes:
- name: kubernetes-dashboard-certs
  secret:
    secretName: kubernetes-dashboard-certs
```

```sh
curl -fsSL https://raw.githubusercontent.com/kubernetes/dashboard/v2.1.0/aio/deploy/recommended.yaml \
  | sed 's/--auto-generate-certificates/--auto-generate-certificates=false/' \
  > kubernetes-dashboard-v2.1.0.yaml
kubectl apply -f kubernetes-dashboard-v2.1.0.yaml

```

### Install with `helm` chart

https://github.com/kubernetes/dashboard/tree/master/aio/deploy/helm-chart/kubernetes-dashboard

[Available Configurations](https://github.com/kubernetes/dashboard/tree/master/aio/deploy/helm-chart/kubernetes-dashboard#configuration)

[Config. by `values.yaml`](https://github.com/kubernetes/dashboard/blob/master/aio/deploy/helm-chart/kubernetes-dashboard/values.yaml)

```bash
helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard
helm install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard \
  --namespace=kubernetes-dashboard \
  --create-namespace \
  --set image.repository=kubernetesui/dashboard \
  --set image.tag=v2.1.0 \
  --set ingress.enabled=false \
  --set metrics-server.enabled=false
```

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  annotations:
    meta.helm.sh/release-name: kubernetes-dashboard
    meta.helm.sh/release-namespace: kubernetes-dashboard
  creationTimestamp: "2021-02-11T00:50:03Z"
  labels:
    app.kubernetes.io/instance: kubernetes-dashboard
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: kubernetes-dashboard
    app.kubernetes.io/version: 2.1.0
    helm.sh/chart: kubernetes-dashboard-4.0.0
  name: kubernetes-dashboard-certs
  namespace: kubernetes-dashboard
  resourceVersion: "17901371"
  selfLink: /api/v1/namespaces/kubernetes-dashboard/secrets/kubernetes-dashboard-certs
  uid: f6ebbaa3-5410-45b4-b705-bbba632e430c
type: Opaque
EOF
```
kubectl -n kubernetes-dashboard delete secret kubernetes-dashboard-certs
kubectl -n kubernetes-dashboard create secret generic kubernetes-dashboard-certs \
  --from-literal=tls.crt="$(kubectl -n istio-system get secrets ingress-istio-tls-stg -o jsonpath='{.data.tls\.crt}')" \
  --from-literal=tls.key="$(kubectl -n istio-system get secrets ingress-istio-tls-stg -o jsonpath='{.data.tls\.key}')"
  

kubectl -n kubernetes-dashboard patch secret kubernetes-dashboard-certs \
  --type=json -p "
[
  {
    "op": "add",
    "path": "/data",
    "value": "$(kubectl -n istio-system get secrets ingress-istio-tls-stg -o jsonpath="{.data}")"
  }
]"

kubectl -n kubernetes-dashboard patch secret kubernetes-dashboard-certs --type=merge -p "{"data": "$(kubectl -n istio-system get secrets ingress-istio-tls-stg -o jsonpath="{.data}")"}"

helm install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard \
  --namespace=kubernetes-dashboard \
  --create-namespace \
  --set image.repository=kubernetesui/dashboard \
  --set image.tag=v2.1.0 \
  --set protocolHttp=true \
  --set service.externalPort=9090 \
  --set ingress.enabled=false \
  --set metrics-server.enabled=false

  # --create-namespace \  # add it if the namespace is not exist

helm uninstall kubernetes-dashboard --namespace=kubernetes-dashboard
```

```bash
git clone https://github.com/nicholasjackson/mtls-go-example
cd mtls-go-example
./generate kfs.pydemia.org <passwd>
cd ..
mkdir kfs.pydemia.org && mv 1_root 2_intermediate 3_application 4_client ./kfs.pydemia.org
```

```bash
kubectl -n istio-system
    create secret tls istio-ingressgateway-certs \
    --key kfs.pydemia.org/3_application/private/kfs.pydemia.org.key.pem \
    --cert kfs.pydemia.org/3_application/certs/kfs.pydemia.org.cert.pem

kubectl -n istio-system \
    create secret generic istio-ingressgateway-ca-certs \
    --from-file=kfs.pydemia.org/2_intermediate/certs/ca-chain.cert.pem

```

## Set User

### Creaet a Service Account & ClusterRoleBinding

```bash
kubectl apply -f kubernetes-dashboard-sa.yaml

```



### Get a Bearer Token

```bash
kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin | awk '{print $1}')
```

The message would be:

```ascii
Name:         admin-token-x6wbl
Namespace:    kubernetes-dashboard
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: admin
              kubernetes.io/service-account.uid: b46608ce-43c6-4dbb-bdf8-3f7ca38dd896

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1115 bytes
namespace:  20 bytes
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IjdoUjEyZGFuRjZJXzcyZXNHLWtpaFlORkRlV29VMTg0N0FfRnk5ZkU2ZkEifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi10b2tlbi14NndibCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJhZG1pbiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI0NjYwOGNlLTQzYzYtNGRiYi1iZGY4LTNmN2NhMzhkZDg5NiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDphZG1pbiJ9.CytYYh6N_fzqhurTHqTED22VXQNbba-uWzsY3cM626KsWJwdD6TVLUK38U7YZ6bJix43cWHwFEK2zvRHSvXhG4QUUD9u3yrYtMQUAajXBytkCafsqE4KhRJUZNJX6GIaczbbetvODmnSAP-Jeqz4kyxnjoKE8T9g_2N9ScO_jipPQnfCmFxiN0U3rwgnY3QdSB9fiKbWfljh2TA7Y912KXgaU2DtqvwWySGyQIYMpLlKHKfKdE2xnetND5IXSHaJEbKOVPAu3Q22OcJTrfR12YaftC0K_D1mw7mPFO84jlVtEfObdirzBRtXOe8KrShQ8EcM6DJ6kdqwjxhp89lC3w


Name:         default-token-lbf5j
Namespace:    kubernetes-dashboard
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: default
              kubernetes.io/service-account.uid: a8090f90-2db6-4ff8-8d75-f2d9b5c5ce1c

Type:  kubernetes.io/service-account-token

Data
====
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IjdoUjEyZGFuRjZJXzcyZXNHLWtpaFlORkRlV29VMTg0N0FfRnk5ZkU2ZkEifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkZWZhdWx0LXRva2VuLWxiZjVqIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImRlZmF1bHQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJhODA5MGY5MC0yZGI2LTRmZjgtOGQ3NS1mMmQ5YjVjNWNlMWMiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6ZGVmYXVsdCJ9.ICAYQXeNcDHF6ODqIyHahbwMbOmiclCazUyxCf4JdJl-ZjDVoCtBYamgUPrqUiDcJpVFU_xFigjdUpVRSIadgwcwQuCyrZZWudjevjPbvM5UQ8QVlrnDOI_rLPSh79m6ay6iMer2jLuWz4r2QHBzRpxP1mTgtNSZX6uYd7_XDp3fy53gh_BpKBr4fn-KeSL3oe044rFXjePc-8Y3tDAzZzb4GcwJYn8rBRMaHmHIH0-xyK2jK2PDGcOpdJHiPKDqwijrGk8VhCYwCeA36cA7w3fGYahSHX-4G_JSN5i9QHa8LwyDbLlRgySv1Kt5JueWYXU2Anf0Q91odKH0l3TSag
ca.crt:     1115 bytes
namespace:  20 bytes


Name:         kubernetes-dashboard-certs
Namespace:    kubernetes-dashboard
Labels:       k8s-app=kubernetes-dashboard
Annotations:  
Type:         Opaque

Data
====


Name:         kubernetes-dashboard-csrf
Namespace:    kubernetes-dashboard
Labels:       k8s-app=kubernetes-dashboard
Annotations:  
Type:         Opaque

Data
====
csrf:  256 bytes


Name:         kubernetes-dashboard-key-holder
Namespace:    kubernetes-dashboard
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
priv:  1679 bytes
pub:   459 bytes


Name:         kubernetes-dashboard-token-2ff9q
Namespace:    kubernetes-dashboard
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: kubernetes-dashboard
              kubernetes.io/service-account.uid: 999ab2bc-ae8d-4b59-9cf2-5c3966183ffb

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1115 bytes
namespace:  20 bytes
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IjdoUjEyZGFuRjZJXzcyZXNHLWtpaFlORkRlV29VMTg0N0FfRnk5ZkU2ZkEifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZC10b2tlbi0yZmY5cSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6Ijk5OWFiMmJjLWFlOGQtNGI1OS05Y2YyLT
```



## with HTTP

### 

## with HTTPS

### Create a secret

```bash
kubectl create secret generic kubernetes-dashboard-certs --from-file=./certs -n kube-system
```

---
```bash
wget https://raw.githubusercontent.com/kubernetes/dashboard/v1.10.1/src/deploy/recommended/kubernetes-dashboard.yaml

vi kubernetes-dashboard.yaml
# ------------------- Dashboard Service ------------------- #
kind: Service
apiVersion: v1
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kube-system
spec:
  type: LoadBalancer # <-- 추가
  ports:
    - port: 443
      targetPort: 8443
  selector:
    k8s-app: kubernetes-dashboard
```

```bash
kubectl apply -f kubernetes-dashboard.yaml
```

## Create admin

```bash
kubectl apply -f <<EOF
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kube-system
EOF
```
