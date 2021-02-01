
# Upgrade Knative: `0.17.0` to `0.18.0`

https://github.com/knative/docs/blob/release-0.18/docs/install/upgrade-installation.md

```bash
mkdir -p knative/v0.17.0-to-v0.18.0 && \
cd knative/v0.17.0-to-v0.18.0
```


```bash
kubectl get pods --namespace knative-serving
kubectl get pods --namespace knative-eventing
```

## Pre-install: `knative-eventing`

```bash
curl -fsSL https://github.com/knative/eventing/releases/download/v0.18.0/eventing-pre-install-jobs.yaml -O && \
  kubectl apply -f eventing-pre-install-jobs.yaml
```

## Upgrade(Install) `0.18.0`

```bash
# knative-serving
mkdir -p knative-serving && \
  cd knative-serving && \
  curl -fsSL https://github.com/knative/serving/releases/download/v0.18.0/serving-crds.yaml -O && \
  kubectl apply -f serving-crds.yaml &&
  curl -fsSL https://github.com/knative/serving/releases/download/v0.18.0/serving-core.yaml -O && \
  curl -fsSL https://github.com/knative/net-istio/releases/download/v0.18.0/release.yaml -O && \
  curl -fsSL https://github.com/knative/net-certmanager/releases/download/v0.18.0/release.yaml -O && \
  cd .. && kubectl apply -f knative-serving

# knative-eventing
mkdir -p knative-eventing && \
  cd knative-eventing && \
  curl -fsSL https://github.com/knative/eventing/releases/download/v0.18.0/eventing-crds.yaml -O && \
  curl -fsSL https://github.com/knative/eventing/releases/download/v0.18.0/eventing-core.yaml -O && \
  curl -fsSL https://github.com/knative/eventing/releases/download/v0.18.0/in-memory-channel.yaml -O && \
  curl -fsSL "https://github.com/knative/eventing-contrib/releases/download/v0.18.0/kafka-channel.yaml" \
  | sed 's/REPLACE_WITH_CLUSTER_URL/my-cluster-kafka-bootstrap.kafka:9092/' > kafka-channel.yaml && \
  curl -fsSL https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v0.18.0/eventing-kafka-controller.yaml -O && \
  curl -fsSL https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v0.18.0/eventing-kafka-broker.yaml -O && \
  cd .. && kubectl apply -f knative-eventing
```

## Post Install: `knative-serving`

```bash
curl -fsSL https://github.com/knative/serving/releases/download/v0.18.0/serving-post-install-jobs.yaml -O && \
  kubectl apply -f serving-post-install-jobs.yaml
```


## Post Install: `knative-eventing`

```bash
# Non-exist
# curl -fsSL https://github.com/knative/eventing/releases/download/v0.18.0/eventing-post-install-jobs.yaml -O && \
#   kubectl apply -f eventing-post-install-jobs.yaml
```


```bash
kubectl delete -f eventing-pre-install-jobs.yaml && \
kubectl delete -f serving-post-install-jobs.yaml
# kubectl delete -f eventing-post-install-jobs.yaml

kubectl -n knative-eventing delete job storage-version-migration
kubectl -n knative-eventing delete job storage-version-migration-eventing
```
