#!/bin/bash

set -e
set -o errexit
set -o nounset
set -o pipefail


KUBECTL_VERSION=1.20.0
ISTIO_VERSION=1.7.7
KNATIVE_VERSION=v0.20.0
KFSERVING_VERSION=v0.5.0-rc2


DOWNLOAD_COMMAND=""
function set_download_command () {
  # Try curl.
  if command -v curl > /dev/null; then
    if curl --version | grep Protocols  | grep https > /dev/null; then
      DOWNLOAD_COMMAND="curl -fLSs --retry 5 --retry-delay 1 --retry-connrefused"
      return
    fi
    echo curl does not support https, will try wget for downloading files.
  else
    echo curl is not installed, will try wget for downloading files.
  fi

  # Try wget.
  if command -v wget > /dev/null; then
    DOWNLOAD_COMMAND="wget -qO -"
    return
  fi
  echo wget is not installed.

  echo Error: curl is not installed or does not support https, wget is not installed. \
       Cannot download envoy. Please install wget or add support of https to curl.
  exit 1
}

KUBECTL_COMMAND="kubectl"
function set_kubectl () {
  KUBECTL_VERSION="$1"
  KUBECTL_CURRENT_VER=$(kubectl version --client | grep -oP 'GitVersion:\"v\K[0-9.][^"]+')
  if [ $(version "${KUBECTL_VERSION}") -ge $(version $KUBECTL_CURRENT_VER) ]; then
    echo "'kubectl' version is lower than ${KUBECTL_VERSION}. Downloading kubectl=${KUBECTL_VERSION}..."
    ${DOWNLOAD_COMMAND} -O https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl
    chmod +x kubectl
    mkdir -p $HOME/.local/bin
    export PATH="$HOME/.local/bin:${PATH}"
    mv kubectl $HOME/.local/bin/kubectl
    echo "'kubectl' is downloaded: `which kubectl`"
  else
    echo "Current \'kubectl version\' is satisfied."
  fi
}


function set_istioctl () {
  ISTIO_VERSION="$1"
  echo "Downloading istioctl=${ISTIO_VERSION}..."
  time $(${DOWNLOAD_COMMAND} https://git.io/getLatestIstio | sh -)
  cd istio-${ISTIO_VERSION}
  chmod +x istioctl
  mkdir -p $HOME/.local/bin
  export PATH="$HOME/.local/bin:${PATH}"
  mv kubectl $HOME/.local/bin/kubectl
  echo "'istioctl' is downloaded: `which istioctl`"
}


function get_istio_yaml () {
  # 'basic' or ${profile_name}
  mkdir -p ./istio
  if [[ "basic" == "$1" ]]; then
    echo "Generating istio operator for \'kfserving basic\'..."
    cat << EOF > ./istio/istio-core.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: istio-system
  labels:
    istio-injection: disabled
---
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  values:
    global:
      proxy:
        autoInject: disabled
      useMCP: false
      # The third-party-jwt is not enabled on all k8s.
      # See: https://istio.io/docs/ops/best-practices/security/#configure-third-party-service-account-tokens
      jwtPolicy: first-party-jwt

  addonComponents:
    pilot:
      enabled: true
    tracing:
      enabled: true
    kiali:
      enabled: true
    prometheus:
      enabled: true
    grafana:
      enabled: true

  components:
    ingressGateways:
      - name: istio-ingressgateway
        enabled: true
      - name: cluster-local-gateway
        enabled: true
        label:
          istio: cluster-local-gateway
          app: cluster-local-gateway
        k8s:
          service:
            type: ClusterIP
            ports:
            - port: 15020
              name: status-port
            - port: 80
              #targetPort: 80
              name: http2
            - port: 443
              #targetPort: 443
              name: https
            - port: 15029
              name: kiali
            - port: 15030
              name: prometheus
            - port: 15031
              name: grafana
            - port: 15032
              name: tracing
            - port: 15035
              name: knative-grafana
EOF
    echo "\'istio/istio-core.yaml\' is generated."
  else
    echo "Generating istio manifest for profile=\'"$1"\'..."
    cat << EOF > ./istio/istio-core.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: istio-system
  labels:
    istio-injection: disabled
---
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  values:
    global:
      proxy:
        autoInject: enabled
      useMCP: true
      # The third-party-jwt is not enabled on all k8s.
      # See: https://istio.io/docs/ops/best-practices/security/#configure-third-party-service-account-tokens
      jwtPolicy: first-party-jwt

  addonComponents:
    pilot:
      enabled: true

  components:
    ingressGateways:
      - name: istio-ingressgateway
        enabled: true
      - name: cluster-local-gateway
        enabled: true
        label:
          istio: cluster-local-gateway
          app: cluster-local-gateway
        k8s:
          service:
            type: ClusterIP
            ports:
            - port: 15020
              name: status-port
            - port: 80
              #targetPort: 80
              name: http2
            - port: 443
              #targetPort: 443
              name: https
            - port: 15029
              name: kiali
            - port: 15030
              name: prometheus
            - port: 15031
              name: grafana
            - port: 15032
              name: tracing
            - port: 15035
              name: knative-grafana
EOF
    istioctl manifest generate \
      -f istio/istio-core.yaml \
      --set profile="$1" \
      >> istio-core.yaml
    echo "\'istio/istio-core.yaml\' is generated."
  fi
}

function install_istio () {
  istioctl install \
    -f ./istio/istio-core.yaml \
    --set values.gateways.istio-ingressgateway.runAsRoot=true > /dev/tty
}

function get_istio_metrics_yaml () {
  ISTIO_VERSION="$1"
  ISTIO_RELEASE=$(echo ${ISTIO_VERSION} | grep -oP '[0-9]+.[0-9]+')
  mkdir -p ./istio
  cd ./istio && \
  ${DOWNLOAD_COMMAND} https://raw.githubusercontent.com/istio/istio/release-${ISTIO_RELEASE}/samples/addons/grafana.yaml -O && \
  ${DOWNLOAD_COMMAND} https://raw.githubusercontent.com/istio/istio/release-${ISTIO_RELEASE}/samples/addons/jaeger.yaml -O && \
  ${DOWNLOAD_COMMAND} https://raw.githubusercontent.com/istio/istio/release-${ISTIO_RELEASE}/samples/addons/kiali.yaml -O && \
  ${DOWNLOAD_COMMAND} https://raw.githubusercontent.com/istio/istio/release-${ISTIO_RELEASE}/samples/addons/prometheus.yaml -O && \
  ${DOWNLOAD_COMMAND} https://raw.githubusercontent.com/istio/istio/release-${ISTIO_RELEASE}/samples/addons/extras/zipkin.yaml -O && \
  cd ..
  echo "\'istio-metrics\' manifests are downloaded."
}

function get_knative_yaml () {
  KNATIVE_VERSION="$1"
  mkdir -p ./knative-serving && \
  cd ./knative-serving && \
  ${DOWNLOAD_COMMAND} https://github.com/knative/serving/releases/download/v${KNATIVE_VERSION}/serving-crds.yaml -O && \
  ${DOWNLOAD_COMMAND} https://github.com/knative/serving/releases/download/v${KNATIVE_VERSION}/serving-core.yaml -O && \
  ${DOWNLOAD_COMMAND} https://github.com/knative/net-istio/releases/download/v${KNATIVE_VERSION}/release.yaml -o net-istio-release.yaml && \
  ${DOWNLOAD_COMMAND} https://github.com/knative/net-certmanager/releases/download/v${KNATIVE_VERSION}/release.yaml -o net-certmanager-release.yaml && \
  cd .. > dev/tty
  echo "\'knative-serving\' manifests are downloaded."

  mkdir -p ./knative-eventing && \
    cd ./knative-eventing && \
    ${DOWNLOAD_COMMAND} https://github.com/knative/eventing/releases/download/v${KNATIVE_VERSION}/eventing-crds.yaml -O && \
    ${DOWNLOAD_COMMAND} https://github.com/knative/eventing/releases/download/v${KNATIVE_VERSION}/eventing-core.yaml -O && \
    ${DOWNLOAD_COMMAND} https://github.com/knative/eventing/releases/download/v${KNATIVE_VERSION}/in-memory-channel.yaml -O && \
    ${DOWNLOAD_COMMAND} "https://github.com/knative-sandbox/eventing-kafka/releases/download/v${KNATIVE_VERSION}/channel-consolidated.yaml" \
    | sed 's/REPLACE_WITH_CLUSTER_URL/my-cluster-kafka-bootstrap.kafka:9092/' > channel-consolidated.yaml && \
    ${DOWNLOAD_COMMAND} https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v${KNATIVE_VERSION}/eventing-kafka-controller.yaml -O && \
    ${DOWNLOAD_COMMAND} https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v${KNATIVE_VERSION}/eventing-kafka-broker.yaml -O && \
    ${DOWNLOAD_COMMAND} https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/v${KNATIVE_VERSION}/eventing-kafka-sink.yaml -O && \
    ${DOWNLOAD_COMMAND} https://github.com/knative-sandbox/eventing-kafka/releases/download/v${KNATIVE_VERSION}/source.yaml -O && \
    cd .. > dev/tty
    echo "\'knative-eventing\' manifests are downloaded."
}

function get_certmanager_yaml () {
  CM_VERSION="$1"
  mkdir -p ./cert-manager && \
    cd ./cert-manager && \
    ${DOWNLOAD_COMMAND} https://github.com/jetstack/cert-manager/releases/download/v${CM_VERSION}/cert-manager.yaml -O && \
    cd .. > dev/tty
    echo "\'cert-manager\' manifests are downloaded."
}

function install_certmanager () {
  ${KUBECTL_COMMAND} apply -f ./cert-manager > /dev/tty
  ${KUBECTL_COMMAND} wait --for=condition=available --timeout=600s deployment/cert-manager-webhook -n cert-manager > /dev/tty
}


function install_istio () {
  ${KUBECTL_COMMAND} apply -f ./istio > /dev/tty
}


function install_knative () {
  ${KUBECTL_COMMAND} apply -f ./knative-serving > /dev/tty
  ${KUBECTL_COMMAND} apply -f ./knative-eventing > /dev/tty
}

function get_kfserving_yaml () {
  KFSERVING_VERSION="$1"
  ${DOWNLOAD_COMMAND} https://raw.githubusercontent.com/pydemia/kfserving/master/install/${KFSERVING_VERSION}/kfserving.yaml -O > /dev/tty
}


function install_kfserving () {
  K8S_MINOR=$(${KUBECTL_COMMAND} version | perl -ne 'print $1."\n" if /Server Version:.*?Minor:"(\d+)"/')
  if [[ $K8S_MINOR -lt 16 ]]; then
    ${KUBECTL_COMMAND} apply -f kfserving.yaml --validate=false > /dev/tty
  else
    ${KUBECTL_COMMAND} apply -f kfserving.yaml > /dev/tty
  fi
}

function setup () {
  CERT_MANAGER_VERSION=1.1.1
  KUBECTL_VERSION=1.20.0
  ISTIO_VERSION=1.7.7
  KNATIVE_VERSION=0.20.0
  KFSERVING_VERSION=v0.5.0-rc2

  set_download_command
  set_kubectl $KUBECTL_VERSION
  set_istioctl $ISTIO_VERSION

  get_certmanager_yaml $CERT_MANAGER_VERSION
  get_istio_yaml demo # 'basic' or ${profile_name}
  get_istio_metrics_yaml
  get_knative_yaml $KNATIVE_VERSION
  get_kfserving_yaml $KFSERVING_VERSION

}

function install () {
  install_certmanager
  install_istio
  install_knative
  install_kfserving
}

setup
install
