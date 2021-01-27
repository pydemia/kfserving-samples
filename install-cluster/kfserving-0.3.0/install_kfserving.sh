
#!/bin/bash

kubectl create clusterrolebinding cluster-admin-binding \
    --clusterrole=cluster-admin \
    --user=$(gcloud config get-value core/account)
  

CERT_MANAGER_VERSION="v0.15.0"
#ISTIO_VERSION="1.4.1"
ISTIO_VERSION="1.4.6"
KNATIVE_VERSION="v0.14.0"
KFSERVING_VERSION="v0.3.0"

PWD_GLOBAL_START="$(pwd)"
mkdir -p kfserving_pkg;cd kfserving_pkg

#######################################
# cert-manager: $CERT_MANAGER_VERSION
#######################################
echo "
############################
# cert-manager: $CERT_MANAGER_VERSION
############################
"

DIR="cert-manager-${CERT_MANAGER_VERSION}"
mkdir -p ${DIR};cd ${DIR}

curl -sL https://github.com/jetstack/cert-manager/releases/download/${CERT_MANAGER_VERSION}/cert-manager.yaml -O && \
  kubectl apply --validate=false -f cert-manager.yaml

cd ..
sleep 20
############################################
# Istio, for Knative setup
############################################
echo "
############################################
# Istio, for Knative setup($ISTIO_VERSION)
############################################
"
curl -sL https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh -
cd istio-${ISTIO_VERSION}

# Install CRDs
for i in install/kubernetes/helm/istio-init/files/crd*yaml; do kubectl apply -f $i; done

# Create namespace `istio-system`
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: istio-system
  labels:
    istio-injection: disabled
EOF

# Installing Istio without sidecar injection(Recommended default installation)
# A lighter template, with just pilot/gateway.
# Based on install/kubernetes/helm/istio/values-istio-minimal.yaml

# helm template --namespace=istio-system \
#   --set prometheus.enabled=false \
#   --set mixer.enabled=false \
#   --set mixer.policy.enabled=false \
#   --set mixer.telemetry.enabled=false \
#   `# Pilot doesn't need a sidecar.` \
#   --set pilot.sidecar=false \
#   --set pilot.resources.requests.memory=128Mi \
#   `# Disable galley (and things requiring galley).` \
#   --set galley.enabled=false \
#   --set global.useMCP=false \
#   `# Disable security / policy.` \
#   --set security.enabled=false \
#   --set global.disablePolicyChecks=true \
#   `# Disable sidecar injection.` \
#   --set sidecarInjectorWebhook.enabled=false \
#   --set global.proxy.autoInject=disabled \
#   --set global.omitSidecarInjectorConfigMap=true \
#   --set gateways.istio-ingressgateway.autoscaleMin=1 \
#   --set gateways.istio-ingressgateway.autoscaleMax=2 \
#   `# Set pilot trace sampling to 100%` \
#   --set pilot.traceSampling=100 \
#   --set global.mtls.auto=false \
#   install/kubernetes/helm/istio \
#   > ./istio-lean.yaml

helm template --namespace=istio-system \
  --set prometheus.enabled=true \
  --set kiali.enabled=true \
  --set grafana.enabled=true \
  --set tracing.enabled=true \
  --set mixer.enabled=true \
  --set mixer.policy.enabled=true \
  --set mixer.telemetry.enabled=true \
  `# Pilot doesn't need a sidecar.` \
  --set pilot.sidecar=false \
  --set pilot.resources.requests.memory=128Mi \
  `# Disable galley (and things requiring galley).` \
  --set galley.enabled=false \
  --set global.useMCP=false \
  `# Disable security / policy.` \
  --set security.enabled=false \
  --set global.disablePolicyChecks=true \
  `# Disable sidecar injection.` \
  --set sidecarInjectorWebhook.enabled=false \
  --set global.proxy.autoInject=disabled \
  --set global.omitSidecarInjectorConfigMap=true \
  --set gateways.istio-ingressgateway.autoscaleMin=1 \
  --set gateways.istio-ingressgateway.autoscaleMax=2 \
  `# Set pilot trace sampling to 100%` \
  --set pilot.traceSampling=100 \
  --set global.mtls.auto=false \
  install/kubernetes/helm/istio \
  > ./istio-lean.yaml

kubectl apply -f istio-lean.yaml

# Setup cluster-local-gateway
# Add the extra gateway.
helm template --namespace=istio-system \
  --set gateways.custom-gateway.autoscaleMin=1 \
  --set gateways.custom-gateway.autoscaleMax=2 \
  --set gateways.custom-gateway.cpu.targetAverageUtilization=60 \
  --set gateways.custom-gateway.labels.app='cluster-local-gateway' \
  --set gateways.custom-gateway.labels.istio='cluster-local-gateway' \
  --set gateways.custom-gateway.type='ClusterIP' \
  --set gateways.istio-ingressgateway.enabled=false \
  --set gateways.istio-egressgateway.enabled=false \
  --set gateways.istio-ilbgateway.enabled=false \
  --set global.mtls.auto=false \
  install/kubernetes/helm/istio \
  -f install/kubernetes/helm/istio/example-values/values-istio-gateways.yaml \
  | sed -e "s/custom-gateway/cluster-local-gateway/g" -e "s/customgateway/clusterlocalgateway/g" \
  > ./istio-local-gateway.yaml

kubectl apply -f istio-local-gateway.yaml


curl -sL https://raw.githubusercontent.com/knative/serving/master/third_party/istio-1.4.9/istio-knative-extras.yaml -O && \
    kubectl apply -f istio-knative-extras.yaml

cd ..
sleep 90
##################################
# Knative
##################################

echo "
##################################
# Knative: $KNATIVE_VERSION
##################################
"
DIR="knative-${KNATIVE_VERSION}"
mkdir -p $DIR;cd $DIR

# 1. Install the `CRDs(Custom Resource Definitions)`
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-crds.yaml -O && \
    kubectl apply -f serving-crds.yaml
# 2. Install the core components of `Serving`
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-core.yaml -O && \
    kubectl apply -f serving-core.yaml

sleep 30
# 3-1. Install the Knative Istio controller:
curl -sL https://github.com/knative/net-istio/releases/download/${KNATIVE_VERSION}/release.yaml -o serving-istio.yaml && \
    kubectl apply --filename serving-istio.yaml --request-timeout="3m"

curl -sL https://github.com/knative/net-istio/releases/download/${KNATIVE_VERSION}/net-istio.yaml -O && \
    kubectl apply --filename net-istio.yaml --request-timeout="3m"

# v0.13.0[NAME CHANGED]
# curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-istio.yaml -O && \
#     kubectl apply -f serving-istio.yaml

kubectl --namespace istio-system get service istio-ingressgateway
# # 4. Configure DNS: Magic DNS (`xip.io`)
# curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-default-domain.yaml -O && \
#     kubectl apply -f serving-default-domain.yaml

curl -sL https://github.com/knative/serving/releases/download/v0.14.0/serving-default-domain.yaml -O && \
    kubectl apply --filename serving-default-domain.yaml

# 4. Real DNS
# 4-A. If the networking layer produced an External IP address,
# then configure a wildcard A record for the domain:
# (Here knative.example.com is the domain suffix for your cluster)
# *.knative.example.com == A 35.233.41.212
# 4-B. If the networking layer produced a CNAME,
# then configure a CNAME record for the domain:
# *.knative.example.com == CNAME a317a278525d111e89f272a164fd35fb-1510370581.eu-central-1.elb.amazonaws.com

# # Replace knative.example.com with your domain suffix
# kubectl patch configmap/config-domain \
#   --namespace knative-serving \
#   --type merge \
#   --patch '{"data":{"knative.example.com":""}}'

# 5. Monitor all Knative components are running:
kubectl get pods --namespace knative-serving

sleep 90
# 6. Optional Serving extensions
# HPA autoscaling(Horizontal Pod Autoscaler)
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-hpa.yaml -O && \
    kubectl apply -f serving-hpa.yaml
# TLS cert-manager
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-cert-manager.yaml -O && \
    kubectl apply -f serving-cert-manager.yaml
# TLS cert-manager OPTION: Enable Auto TLS: ClusterIssuer for HTTP-01 challenge
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: letsencrypt-http01-issuer
spec:
  acme:
    privateKeySecretRef:
      name: letsencrypt
    server: https://acme-v02.api.letsencrypt.org/directory
    solvers:
    - http01:
       ingress:
         class: istio
EOF
# TLS via HTTP01
curl https://github.com/knative/net-http01/releases/download/${KNATIVE_VERSION}/release.yaml -O serving-http01.yaml && \
    kubectl apply --filename serving-http01.yaml
wget https://github.com/knative/net-http01/releases/download/v0.14.0/release.yaml -O serving-http01.yaml && \
    kubectl apply --filename serving-http01.yaml
# TLS wildcard
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/serving-nscert.yaml -O && \
    kubectl apply -f serving-nscert.yaml

sleep 90
# 7. Eventing Components
curl -sL https://github.com/knative/eventing/releases/download/${KNATIVE_VERSION}/eventing-crds.yaml -O && \
    kubectl apply -f eventing-crds.yaml
curl -sL https://github.com/knative/eventing/releases/download/${KNATIVE_VERSION}/eventing-core.yaml -O && \
    kubectl apply -f eventing-core.yaml

# Install a default Channel (messaging) layer: Kafka Case
## Install Apache Kafka for Kubernetes
curl -sL https://knative.dev/docs/eventing/samples/kafka/kafka_setup.sh -o kafka_setup_for_knative.sh && \
  chmod +x kafka_setup_for_knative.sh; ./kafka_setup_for_knative.sh
# kubectl create namespace kafka
# ## Install the Strimzi operator
# curl -L "https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.16.2/strimzi-cluster-operator-0.16.2.yaml" \
#   | sed 's/namespace: .*/namespace: kafka/' \
#   | kubectl -n kafka apply -f -
# kubectl apply -n kafka -f kafka.yaml
## Install the Apache Kafka Channel
curl -L "https://github.com/knative/eventing-contrib/releases/download/${KNATIVE_VERSION}/kafka-channel.yaml" \
 | sed 's/REPLACE_WITH_CLUSTER_URL/my-cluster-kafka-bootstrap.kafka:9092/' \
 | kubectl apply --filename -

## Install a Broker (eventing) layer: Channel-based, Kafka Channel
curl -sL https://github.com/knative/eventing/releases/download/${KNATIVE_VERSION}/channel-broker.yaml -O && \
    kubectl apply -f channel-broker.yaml
# To customize which broker channel implementation is used,
# update the following ConfigMap to specify which configurations are used for which namespaces:
# ConfigMap: `config-br-defaults`

curl -sL https://github.com/knative/eventing-contrib/releases/download/${KNATIVE_VERSION}/kafka-source.yaml -O && \
    kubectl apply -f kafka-source.yaml

# # GCP Pub/Sub Case
# curl -sL https://github.com/google/knative-gcp/releases/download/${KNATIVE_VERSION}/cloud-run-events.yaml -O && \
#     kubectl apply -f cloud-run-events.yaml
# curl -sL https://github.com/knative/eventing/releases/download/${KNATIVE_VERSION}/channel-broker.yaml -O && \
#     kubectl apply -f channel-broker.yaml

# # 8. Observability Plugins (FEATURE STATE: deprecated @ Knative v0.14)
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/monitoring-core.yaml -O && \
    kubectl apply -f monitoring-core.yaml
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/monitoring-metrics-prometheus.yaml -O && \
    kubectl apply -f monitoring-metrics-prometheus.yaml
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/monitoring-tracing-zipkin-in-mem.yaml -O && \
    kubectl apply -f monitoring-tracing-zipkin-in-mem.yaml
# curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/monitoring-tracing-jaeger-in-mem.yaml -O && \
#     kubectl apply -f monitoring-tracing-jaeger-in-mem.yaml
curl -sL https://github.com/knative/serving/releases/download/${KNATIVE_VERSION}/monitoring-logs-elasticsearch.yaml O && \
    kubectl apply -f monitoring-logs-elasticsearch.yaml


# curl -sL https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/crds/jaegertracing.io_jaegers_crd.yaml -O && \
#     kubectl apply -f jaegertracing.io__jaegers_crd.yaml
# curl -sL https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/service_account.yaml -O && \
#     kubectl apply -f service_account.yaml
# curl -sL https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role.yaml -O && \
#     kubectl apply -f role.yaml
# curl -sL https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role_binding.yaml -O && \
#     kubectl apply -f role_binding.yaml
# curl -sL https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/operator.yaml -O && \
#     kubectl apply -f operator.yaml

# curl -sL https://github.com/knative/serving/releases/download/v0.13.0/monitoring-tracing-jaeger-in-mem.yaml -O && \
#     kubectl apply -f monitoring-tracing-jaeger-in-mem.yaml

# kubectl delete -f jaegertracing.io__jaegers_crd.yaml
# kubectl delete -f service_account.yaml
# kubectl delete -f role.yaml
# kubectl delete -f role.yaml
# kubectl delete -f role_binding.yaml
# kubectl delete -f operator.yaml

sleep 20
cd ..

##################################
# KFServing
##################################
echo "
##################################
# KFServing: $KFSERVING_VERSION
##################################
"

DIR="kfserving-${KFSERVING_VERSION}"
mkdir -p ${DIR};cd ${DIR}

#wget https://raw.githubusercontent.com/kubeflow/kfserving/master/install/v0.3.0/kfserving.yaml -O "kfserving-${KFSERVING_VERSION}.yaml"
curl -sL https://raw.githubusercontent.com/kubeflow/kfserving/master/install/${KFSERVING_VERSION}/kfserving.yaml \
    -o "kfserving-${KFSERVING_VERSION}.yaml"
kubectl apply -f "kfserving-${KFSERVING_VERSION}.yaml"

# Setting for KFServing pod mutator
kubectl patch \
    mutatingwebhookconfiguration inferenceservice.serving.kubeflow.org \
    --patch '{"webhooks":[{"name": "inferenceservice.kfserving-webhook-server.pod-mutator","objectSelector":{"matchExpressions":[{"key":"serving.kubeflow.org/inferenceservice", "operator": "Exists"}]}}]}'

# Patch config-istio
kubectl -n knative-serving patch configmap/config-istio \
  --type merge \
  --patch \
'{"data": {"gateway.knative-serving.knative-ingress-gateway": "istio-ingressgateway.istio-system.svc.cluster.local","local-gateway.knative-serving.cluster-local-gateway": "cluster-local-gateway.istio-system.svc.cluster.local","local-gateway.mesh": "mesh"}}'

# kubectl -n knative-serving get cm config-istio \
#   -o jsonpath="{.data['gateway\.knative-ingress-gateway']}"

kubectl -n knative-serving get cm config-istio \
  -o jsonpath="{.data['gateway\.knative-serving\.knative-ingress-gateway']}"

cd ..

##################################
# InferenceService
##################################
INFERENCE_NS="ifsvc"
echo 'INFERENCE_NS="ifsvc"'
kubectl create ns $INFERENCE_NS
kubectl label ns $INFERENCE_NS serving.kubeflow.org/inferenceservice=enabled


##################################
# Test: InferenceService
##################################
echo "
##################################
# Test: InferenceService
#   - namespace: 'inference-test'
#   - inference: 'sklearn.yaml'
##################################
"
TEST_IFSVC_NS="inference-test"
kubectl create ns $TEST_IFSVC_NS
kubectl label ns $TEST_IFSVC_NS serving.kubeflow.org/inferenceservice=enabled

curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/sklearn.yaml -O && \
  kubectl -n $TEST_IFSVC_NS apply -f sklearn.yaml

curl -fsSL https://raw.githubusercontent.com/kubeflow/kfserving/master/docs/samples/sklearn/iris-input.json -O

MODEL_NAME=sklearn-iris
INPUT_PATH=@./iris-input.json

kubectl -n $TEST_IFSVC_NS wait --for=condition=ready --timeout=90s\
    inferenceservice $MODEL_NAME
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $TEST_IFSVC_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "$CLUSTER_IP, $SERVICE_HOSTNAME"

curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH

kubectl -n $TEST_IFSVC_NS delete -f sklearn.yaml
kubectl delete ns inference-test

echo "Test has been finished."