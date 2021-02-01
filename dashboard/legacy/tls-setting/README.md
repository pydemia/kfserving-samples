# SSL/TLS Setting via `cert-manager`

## `knative-monitoring`


### Create an Issuer

```yaml
apiVersion: cert-manager.io/v1alpha2
kind: Issuer
metadata:
  name: grafana-ca-issuer
  namespace: knative-monitoring
spec:
#   selfSigned: {}
  ca:
    secretName: grafana-ca
# apiVersion: cert-manager.io/v1
# kind: Issuer
# metadata:
#   name: ca-issuer
#   namespace: mesh-system
# spec:
#   ca:
#     secretName: ca-key-pair
```

```yaml
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1alpha2
kind: Issuer
metadata:
  name: grafana-ca-issuer
  namespace: knative-monitoring
spec:
  selfSigned: {}
#   ca:
#     secretName: grafana-ca
---
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: grafana-cert
  namespace: knative-monitoring
spec:
  commonName: grafana.knative-monitoring.svc
  dnsNames:
  - grafana.knative-monitoring.svc
  - "*.knative-monitoring.svc"
#   - example.com
#   - www.example.com
  issuerRef:
    kind: Issuer
    name: grafana-ca-issuer
  secretName: knative-monitoring-cert
#   duration: 2160h # 90d
#   renewBefore: 360h # 15d
# #   subject:
# #     organizations:
# #     - jetstack
#   isCA: true
#   keySize: 2048
#   keyAlgorithm: rsa
#   keyEncoding: pkcs1
#   usages:
#     - server auth
#     - client auth
#   # At least one of a DNS Name, URI, or IP address is required.
EOF
```

* `<= 0.16`: (`cert-manager.io/v1alpha2`)
```yaml
# apiVersion: cert-manager.io/v1alpha2
# kind: Certificate
# metadata:
#   name: monitoring-cert
# spec:
#   commonName: kfserving-webhook-server-service.kfserving-system.svc
#   dnsNames:
#   - kfserving-webhook-server-service.knative-monitoring.svc
#   issuerRef:
#     kind: Issuer
#     name: selfsigned-issuer
#   secretName: knative-monitoring-cert
---
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: grafana-cert
  namespace: knative-monitoring
spec:
  secretName: knative-monitoring-cert
  commonName: grafana.knative-monitoring.svc
  dnsNames:
  - grafana.knative-monitoring.svc
  - "*.knative-monitoring.svc"
#   - example.com
#   - www.example.com
  issuerRef:
    kind: Issuer
    name: grafana-ca-issuer
#   duration: 2160h # 90d
#   renewBefore: 360h # 15d
#   subject:
#     organizations:
#     - jetstack
  isCA: true
#   keySize: 2048
#   keyAlgorithm: rsa
#   keyEncoding: pkcs1
  usages:
    - server auth
    - client auth
#   # At least one of a DNS Name, URI, or IP address is required.
```

* `>= 1.0`: (`cert-manager.io/v1`)

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: grafana-cert
  namespace: knative-monitoring
spec:
  commonName: grafana.knative-monitoring.svc
  dnsNames:
  - grafana.knative-monitoring.svc
  - "*.knative-monitoring.svc"
#   - example.com
#   - www.example.com
  issuerRef:
    kind: Issuer
    name: grafana-ca-issuer
  secretName: knative-monitoring-cert
#   duration: 2160h # 90d
#   renewBefore: 360h # 15d
# #   subject:
# #     organizations:
# #     - jetstack
#   isCA: true
#   privateKey:
#     algorithm: RSA
#     encoding: PKCS1
#     size: 2048
  usages:
    - server auth
    - client auth
#   # At least one of a DNS Name, URI, or IP address is required.

```

Get `crt` to local:

```bash
kubectl -n knative-monitoring get secrets knative-monitoring-cert -o jsonpath='{.data.tls\.crt}' | base64 -d > grafana.crt
```

---
## Istio-ingressgateway


### Self-Made CA
```bash
openssl req -x509 -newkey rsa:2048 -nodes -keyout airuntime.key -days 365 -out airuntime.crt -subj "/CN=*.pydemia.org"
# openssl genrsa -out server.key 2048
kubectl -n istio-system create secret tls airuntime-https-ca \
  --cert airuntime.crt --key airuntime.key

```

```yml
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1alpha2
kind: Issuer
metadata:
  name: istio-ca-issuer
  namespace: knative-monitoring
spec:
  # selfSigned: {}
  ca:
    secretName: airuntime-https-ca
EOF
```

### Made by `cert-manager`

```yaml
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1alpha2
kind: Issuer
metadata:
  name: istio-ca-issuer
  namespace: istio-system
  labels:
    app: airuntime
spec:
  selfSigned: {}
#   ca:
#     secretName: grafana-ca
---
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: istio-ca-cert
  namespace: istio-system
  labels:
    app: airuntime
spec:
  secretName: istio-https-cert
  commonName: "air-kf2-ingress.pydemia.org"
  dnsNames:
  - "air-kf2-ingress.pydemia.org"
  issuerRef:
    kind: Issuer
    name: istio-ca-issuer
  isCA: true
  keySize: 2048
  keyAlgorithm: rsa
  keyEncoding: pkcs1
  usages:
    - server auth
    - client auth
#   # At least one of a DNS Name, URI, or IP address is required.
EOF

```

Verify it:

```bash
kubectl -n istio-system get certificates.cert-manager.io
kubectl -n istio-system get secrets
kubectl -n istio-system delete certificates.cert-manager.io istio-ca-cert
kubectl -n istio-system delete secret istio-https-cert
```

```bash
SECRET_NAME="istio-https-cert"
openssl verify -CAfile \
<(kubectl -n istio-system get secret $SECRET_NAME \
  -o jsonpath='{.data.ca\.crt}' | base64 -d) \
<(kubectl -n istio-system get secret $SECRET_NAME \
  -o jsonpath='{.data.tls\.crt}' | base64 -d)
```

Get `crt` to local:

```bash
kubectl -n istio-system get secrets istio-https-cert -o jsonpath='{.data.tls\.crt}' | base64 -d > istio-https-kf2.crt

# MUTUAL
kubectl -n istio-system get secrets istio-https-cert -o jsonpath='{.data.ca\.crt}' | base64 -d > istio-https-kf2-ca.crt
```

> :warning: Istio supports reading a few different Secret formats, to support integration with various tools such as cert-manager:
> 
> - A TLS Secret with keys `tls.key` and `tls.crt`, as described above. For mutual TLS, a `ca.crt` key can be used.
> - A generic Secret with keys key and cert. For mutual TLS, a `cacert `key can be used.
> - A generic Secret with keys key and cert. For mutual TLS, a separate generic Secret named `<secret>-cacert`, with a `cacert` key. For example, `httpbin-credential` has key and cert, and `httpbin-credential-cacert` has cacert.

* [](https://istio.io/latest/docs/tasks/traffic-management/ingress/secure-ingress/#configure-a-mutual-tls-ingress-gateway)

```bash
kubectl apply -f expose-knative-monitoring-with-tls.yaml
```


---

## kubernetes-dashboard

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1alpha2
kind: Issuer
metadata:
  name: dashboard-ca-issuer
  namespace: kubernetes-dashboard
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: dashboard-ca-cert
  namespace: kubernetes-dashboard
spec:
  commonName: kubernetes-dashboard.kubernetes-dashboard.svc
  dnsNames:
  - kubernetes-dashboard.kubernetes-dashboard.svc
  - "*.kubernetes-dashboard.svc"
#   - example.com
#   - www.example.com
  issuerRef:
    kind: Issuer
    name: dashboard-ca-issuer
  secretName: dashboard-ca-cert
```

---

## Create a TLS certificate

```bash
kubectl create secret tls my-tls-secret \
  --cert=path/to/cert/file \
  --key=path/to/key/file
```


---

## Use the Secret in a Pod
The Deployment definition below shows how to use the Secret above within a Pod.

```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: somename
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: appname
    spec:
      containers:
      - image: username/img
        name: somename

        volumeMounts:
        - name: tls
          mountPath: /usr/src/app/tls

      volumes:
      - name: tls
        secret:
          secretName: secret-name
```