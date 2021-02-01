
# Upgrade Knative: `0.19.0` to `0.20.0`

https://github.com/knative/docs/blob/release-0.20/docs/install/upgrade-installation.md

```bash
mkdir -p knative/v0.19.0-to-v0.20.0 && \
cd knative/v0.19.0-to-v0.20.0
```


```bash
kubectl get pods --namespace knative-serving
kubectl get pods --namespace knative-eventing
```

## Pre-install: `knative-eventing`

```bash
# Non-exist
# curl -fsSL https://github.com/knative/eventing/releases/download/v0.20.0/eventing-pre-install-jobs.yaml -O && \
#   kubectl apply -f eventing-pre-install-jobs.yaml
```

## Upgrade(Install) `0.19.0`

```bash
# knative-serving
mkdir -p ./knative-serving && \
  cd ./knative-serving && \
  curl -fsSL https://github.com/knative/serving/releases/download/v0.20.0/serving-crds.yaml -O && \
  curl -fsSL https://github.com/knative/serving/releases/download/v0.20.0/serving-core.yaml -O && \
  curl -fsSL https://github.com/knative/net-istio/releases/download/v0.20.0/release.yaml -o net-istio-release.yaml && \
  curl -fsSL https://github.com/knative/net-certmanager/releases/download/v0.20.0/release.yaml -o net-certmanager-release.yaml && \
  cd .. && kubectl apply -f knative-serving

# knative-eventing

# Field is IMMUTABLE: `eventing-kafka-controller.yaml`
# The Deployment "kafka-webhook-eventing" is invalid: spec.selector: Invalid value: v1.LabelSelector{MatchLabels:map[string]string{"app":"kafka-webhook-eventing"}, MatchExpressions:[]v1.LabelSelectorRequirement(nil)}: field is immutable

kubectl -n knative-eventing delete deployment kafka-webhook-eventing

mkdir -p ./knative-eventing && \
  cd ./knative-eventing && \
  curl -fsSL https://github.com/knative/eventing/releases/download/v0.20.0/eventing-crds.yaml -O && \
  curl -fsSL https://github.com/knative/eventing/releases/download/v0.20.0/eventing-core.yaml -O && \
  curl -fsSL https://github.com/knative/eventing/releases/download/v0.20.0/in-memory-channel.yaml -O && \
  curl -fsSL "https://github.com/knative-sandbox/eventing-kafka/releases/download/v0.20.0/channel-consolidated.yaml" \
  | sed 's/REPLACE_WITH_CLUSTER_URL/my-cluster-kafka-bootstrap.kafka:9092/' > channel-consolidated.yaml && \
  curl -fsSL https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v0.20.0/eventing-kafka-controller.yaml -O && \
  curl -fsSL https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v0.20.0/eventing-kafka-broker.yaml -O && \
  curl -fsSL https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v0.20.0/eventing-kafka-sink.yaml -O && \
  curl -fsSL https://github.com/knative-sandbox/eventing-kafka/releases/download/v0.20.0/source.yaml -O && \
  cd .. && kubectl apply -f knative-eventing
```

## Post Install: `knative-serving`

```bash
curl -fsSL https://github.com/knative/serving/releases/download/v0.20.0/serving-post-install-jobs.yaml -O && \
  kubectl apply -f serving-post-install-jobs.yaml
```


## Post Install: `knative-eventing`

```bash
# Non-exist
# curl -fsSL https://github.com/knative/eventing/releases/download/v0.20.0/eventing-post-install-jobs.yaml -O && \
#   kubectl apply -f eventing-post-install-jobs.yaml

mkdir -p knative-eventing-postinstall && \
  cd knative-eventing-postinstall && \
curl -fsSL https://raw.githubusercontent.com/knative/eventing/release-0.20/config/post-install/clusterrole.yaml -O && \
curl -fsSL https://raw.githubusercontent.com/knative/eventing/release-0.20/config/post-install/serviceaccount.yaml -O && \
curl -fsSL https://raw.githubusercontent.com/knative/eventing/release-0.20/config/post-install/storage-version-migrator.yaml -O && \
  cd .. && kubectl apply -f knative-eventing-postinstall
  
```


```bash
kubectl delete -f serving-post-install-jobs.yaml && \
kubectl delete -f knative-eventing-postinstall

kubectl -n knative-eventing delete job storage-version-migration
kubectl -n knative-eventing delete job storage-version-migration-eventing
```

---

## `monitoring kn-eventing broker`

```bash
mkdir -p monitoring-kn-eventing-broker && \
  cd monitoring-kn-eventing-broker && \
  curl -fsSL https://raw.githubusercontent.com/knative/eventing/release-0.20/config/monitoring/metrics/grafana/100-grafana-dash-eventing.yaml -O && \
  curl -fsSL https://raw.githubusercontent.com/knative/eventing/release-0.20/config/monitoring/metrics/prometheus/100-prometheus-scrape-kn-eventing.yaml -O && \
  cd .. && kubectl apply -f monitoring-kn-eventing-broker
```