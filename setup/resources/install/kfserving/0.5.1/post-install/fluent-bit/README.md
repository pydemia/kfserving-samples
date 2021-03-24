# Fluent-bit with `helm`

## Installation

```bash
helm repo add fluent https://fluent.github.io/helm-charts

# Create a namespace
NAMESPACE="logging"
kubectl create namespace ${NAMESPACE}

# Create a secret to access Open Distro for Elasticsearch: USERNAME & PASSWORD
kubectl create secret generic es-cred \
  -n ${NAMESPACE} \
  --from-literal=ELASTICSEARCH_USERNAME='xxx' \
  --from-literal=ELASTICSEARCH_PASSWORD='xxx'


helm install fluent-bit fluent/fluent-bit \
  --namespace ${NAMESPACE} \
  --values=custom-values.yaml \
  > install_fluent-bit.log  #  > 2>&1

```

## Set ExternalName for `fluent-bit`

```bash
kubectl -n ${NAMESPACE} apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
spec:
  type: ExternalName
  # externalName: elasticsearch-opendistro-es-data-svc.elasticsearch.svc.cluster.local
  externalName: elasticsearch-opendistro-es-client-service.elasticsearch.svc.cluster.local
  ports:
  - port: 9200
    targetPort: 9200
    protocol: TCP
EOF
```
