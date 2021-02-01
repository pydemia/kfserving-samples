# UPGRADE NOTE


## Upgrade Istio

### istio `1.4` to `1.5`

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

### istio `1.5` to `1.6`

```bash
ISTIO_VERSION=1.6.2
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh - && \
    mkdir -p $HOME/.local/bin && \
    mv istio-${ISTIO_VERSION}/bin/istioctl $HOME/.local/bin/istioctl && \
    rm -r istio-${ISTIO_VERSION}

istioctl upgrade --set profile=minimal --force -y
kubectl rollout restart deployment
```


### istio `1.6` to `1.7`

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

## Knative

https://knative.dev/docs/install/upgrade-installation/


### `0.15.0` to `0.16.0`

https://github.com/knative/docs/blob/release-0.16/docs/install/upgrade-installation.md

```bash
mkdir -p knative/v0.15.0-to-v0.16.0 && \
cd knative/v0.15.0-to-v0.16.0
```


```bash
kubectl get pods --namespace knative-serving
kubectl get pods --namespace knative-eventing
```

#### Pre-install: `knative-eventing`
```bash
mkdir -p knative-eventing-preinstall-v0.16.0 && \
  cd knative-eventing-preinstall-v0.16.0 && \
  curl -fsSL https://raw.githubusercontent.com/knative/eventing/v0.16.0/config/pre-install/v0.16.0/broker.yaml -O && \
  curl -fsSL https://raw.githubusercontent.com/knative/eventing/v0.16.0/config/pre-install/v0.16.0/clusterrole.yaml -O && \
  curl -fsSL https://raw.githubusercontent.com/knative/eventing/v0.16.0/config/pre-install/v0.16.0/pingsource.yaml -O && \
  curl -fsSL https://raw.githubusercontent.com/knative/eventing/v0.16.0/config/pre-install/v0.16.0/serviceaccount.yaml -O && \
  curl -fsSL https://raw.githubusercontent.com/knative/eventing/v0.16.0/config/pre-install/v0.16.0/storage-version-migration.yaml && \
  cd .. && kubectl apply -f knative-eventing-preinstall-v0.16.0
```

#### Upgrade(Install) `0.16.0`

```bash
# knative-serving
https://github.com/knative/serving/releases/download/v0.16.0/serving-crds.yaml
https://github.com/knative/serving/releases/download/v0.16.0/serving-core.yaml
https://github.com/knative/net-istio/releases/download/v0.16.0/release.yaml
https://github.com/knative/net-certmanager/releases/download/v0.16.0/release.yaml
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.16.0/serving-crds.yaml
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.16.0/serving-core.yaml
kubectl apply --filename https://github.com/knative/net-istio/releases/download/v0.16.0/release.yaml
kubectl apply --filename https://github.com/knative/net-certmanager/releases/download/v0.16.0/release.yaml

# knative-eventing
kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.16.0/eventing-crds.yaml
kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.16.0/eventing-core.yaml
kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.16.0/in-memory-channel.yaml
curl -L "https://github.com/knative/eventing-contrib/releases/download/v0.16.0/kafka-channel.yaml" \
 | sed 's/REPLACE_WITH_CLUSTER_URL/my-cluster-kafka-bootstrap.kafka:9092/' \
 | kubectl apply --filename -
kubectl apply --filename https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v0.16.0/eventing-kafka-broker.yaml
```




```bash
  mkdir -p knative-eventing-postinstall-v0.16.0 && \
  cd knative-eventing-postinstall-v0.16.0 && \
  curl -fsSL https://raw.githubusercontent.com/knative/eventing/v0.16.0/config/post-install/v0.16.0/broker-cleanup.yaml -O && \
  cd .. && kubectl apply -f knative-eventing-postinstall-v0.16.0

kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.16.0/eventing-crds.yaml
kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.16.0/eventing-core.yaml
kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.16.0/in-memory-channel.yaml
curl -L "https://github.com/knative-sandbox/eventing-kafka/releases/download/v0.16.0/channel-consolidated.yaml" \
 | sed 's/REPLACE_WITH_CLUSTER_URL/my-cluster-kafka-bootstrap.kafka:9092/' \
 | kubectl apply --filename -
```


kubectl get pods --namespace knative-serving -l serving.knative.dev/release
```