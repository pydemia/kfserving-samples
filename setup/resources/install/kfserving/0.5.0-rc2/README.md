# Install KFServing

```bash
./kfserving-installer setup > setup-kfserving.log 2>&1 &&
  ./kfserving-installer install > install-kfserving.log 2>&1
```

or 

```bash
CERT_MANAGER_VERSION=1.1.0
KUBECTL_VERSION=v1.20.0
ISTIO_VERSION=1.7.7
KNATIVE_VERSION=v0.18.3
KFSERVING_VERSION=KFSERVING_VERSION:-v0.5.0-rc2

./kfserving-installer install
```



:warning: Knative 0.20 deprecated the local cluster gateway and uses the service `knative-local-gateway` which listens on port `8081`.