#!/bin/bash

TLS_OPT="--insecure-skip-tls-verify"
KUBECTL_CMD="kubectl ${TLS_OPT} "

bash -c "
${KUBECTL_CMD} apply -f istio-components/expose-istio-grafana-http.yaml
${KUBECTL_CMD} apply -f istio-components/expose-istio-kiali-http.yaml
${KUBECTL_CMD} apply -f istio-components/expose-istio-prometheus-http.yaml
${KUBECTL_CMD} apply -f istio-components/expose-istio-tracing-http.yaml
" > expose-istio-components.log

bash -c "
${KUBECTL_CMD} apply -f knative-components/expose-knative-monitoring.yaml
${KUBECTL_CMD} apply -f knative-components/expose-knative-zipkin-http.yaml
${KUBECTL_CMD} -n knative-monitoring patch configmap/grafana-custom-config \
    --type merge \
    --patch "$(cat knative-components/patch-knative-monitoring-grafana-custom-config.yaml)"

${KUBECTL_CMD} -n knative-monitoring patch \
    deployment grafana \
    --patch "$(cat knative-components/patch-scaleup-grafana-resources.yaml)"

${KUBECTL_CMD} -n knative-monitoring rollout restart deployment grafana


${KUBECTL_CMD} -n knative-monitoring patch \
    statefulset prometheus-system \
    --type=merge \
    --patch "$(cat knative-components/patch-scaleup-prometheus-resources.yaml)"

${KUBECTL_CMD} -n knative-monitoring rollout restart statefulset prometheus-system

" > expose-knative-components.log

# # NodePort to LoadBalancer
# ${KUBECTL_CMD} -n istio-system patch svc istio-ingressgateway --dry-run=client --type=json -p='
# [
#     {
#         "op": "replace",
#         "path": "/spec/type",
#         "value": "LoadBalancer"
#     }
# ]'

${KUBECTL_CMD} -n istio-system patch svc istio-ingressgateway --type=json -p='
[
    {
        "op": "add",
        "path": "/spec/ports/-",
        "value": {
            "name": "http-kiali",
            "port": 15029,
            "protocol":"TCP",
            "targetPort": 15029
        }
    },
    {
        "op": "add",
        "path": "/spec/ports/-",
        "value": {
            "name": "http-prometheus",
            "port": 15030,
            "protocol":"TCP",
            "targetPort": 15030
        }
    },
    {
        "op": "add",
        "path": "/spec/ports/-",
        "value": {
            "name": "http-grafana",
            "port": 15031,
            "protocol":"TCP",
            "targetPort": 15031
        }
    },
    {
        "op": "add",
        "path": "/spec/ports/-",
        "value": {
            "name": "http-tracing",
            "port": 15032,
            "protocol":"TCP",
            "targetPort": 15032
        }
    },
    {
        "op": "add",
        "path": "/spec/ports/-",
        "value": {
            "name": "zipkin",
            "port": 15033,
            "protocol":"TCP",
            "targetPort": 15033
        }
    },
    {
        "op": "add",
        "path": "/spec/ports/-",
        "value": {
            "name": "knative-prometheus",
            "port": 15034,
            "protocol":"TCP",
            "targetPort": 15034
        }
    },
    {
        "op": "add",
        "path": "/spec/ports/-",
        "value": {
            "name": "knative-grafana",
            "port": 15035,
            "protocol":"TCP",
            "targetPort": 15035
        }
    },
    {
        "op": "add",
        "path": "/spec/ports/-",
        "value": {
            "name": "http-k8s-dashboard",
            "port": 15036,
            "protocol":"TCP",
            "targetPort": 15036
        }
    }
]'
