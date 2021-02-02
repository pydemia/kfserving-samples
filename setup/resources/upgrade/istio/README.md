# Upgrade Istio

## istio `1.4` to `1.5`

https://istio.io/v1.5/docs/setup/upgrade/istioctl-upgrade/

```bash
istioctl manifest versions
istioctl version

ISTIO_VERSION=1.5.10
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh - && \
    mkdir -p $HOME/.local/bin && \
    mv istio-${ISTIO_VERSION}/bin/istioctl $HOME/.local/bin/istioctl && \
    rm -r istio-${ISTIO_VERSION}

# Error: failed to generate IOPS from file: [] for the current version: 1.4.1, error: chart minor version 1.4.1 doesn't match istioctl version 1.5.0, use --force to override
istioctl upgrade --set profile=minimal --force -y
kubectl rollout restart deployment
```

## istio `1.5` to `1.6`

```bash
ISTIO_VERSION=1.6.2
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh - && \
    mkdir -p $HOME/.local/bin && \
    mv istio-${ISTIO_VERSION}/bin/istioctl $HOME/.local/bin/istioctl && \
    rm -r istio-${ISTIO_VERSION}

istioctl upgrade --set profile=minimal --force -y
kubectl rollout restart deployment
```


## istio `1.6` to `1.7`

```bash
ISTIO_VERSION=1.7.7
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh - && \
    mkdir -p $HOME/.local/bin && \
    mv istio-${ISTIO_VERSION}/bin/istioctl $HOME/.local/bin/istioctl && \
    rm -r istio-${ISTIO_VERSION}

# Canary Upgrade
istioctl install --set revision=canary
kubectl get pods -n istio-system -l app=istiod
kubectl get svc -n istio-system -l app=istiod
kubectl get mutatingwebhookconfigurations

istioctl x uninstall --revision 1-6-8
kubectl get pods -n istio-system -l app=istiod
istioctl x uninstall --revision=canary

istioctl proxy-config endpoints $(kubectl -n istio-system get pod -l app=istio-ingressgateway -o jsonpath='{.items..metadata.name}').istio-system --cluster xds-grpc -ojson | grep hostname


istioctl upgrade --set profile=minimal --force --skip-confirmation -y
kubectl rollout restart deployment
```
