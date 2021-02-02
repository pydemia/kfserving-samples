## Upgrade

### Cert-Manager

Regular Process
https://cert-manager.io/docs/installation/upgrading/

```bash
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v0.15.1

kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.15.1/cert-manager.crds.yaml

helm repo add jetstack https://charts.jetstack.io
helm repo update

# helm list | grep cert-manager
# helm list --insecure-skip-tls-verify | grep cert-manager

# helm upgrade --version <version> <release_name> jetstack/cert-manager
helm upgrade --version v0.15.1 cert-manager jetstack/cert-manager
```

* `0.14` to `0.15`
https://cert-manager.io/docs/installation/upgrading/upgrading-0.14-0.15/


### Istio

* `1.5` to `1.6`
https://istio.io/v1.6/docs/setup/upgrade/


### Knative

* `0.14` to `0.15`

https://knative.dev/v0.15-docs/install/upgrade-installation/


```bash
kubectl edit cm config-istio -n knative-serving
kubectl edit cm config-domain --namespace knative-serving
```