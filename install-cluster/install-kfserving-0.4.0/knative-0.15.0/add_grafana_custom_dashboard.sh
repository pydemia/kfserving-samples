kubectl -n knative-monitoring patch deployments grafana --type=json -p='
[
    {
        "op": "add",
        "path": "/spec/template/spec/containers/0/volumeMounts/-",
        "value": {
            "name": "goyun-dashboard",
            "mountPath": "/grafana-dashboard-definition/goyun-dashboard"
        }
    },
    {
        "op": "add",
        "path": "/spec/template/spec/volumes/-",
        "value": {
            "name": "goyun-dashboard",
            "configMap": {"name": "goyun-dashboard"}
        }
    }
]'

kubectl -n knative-monitoring patch configmap grafana-dashboards --type=merge --patch "$(cat patch_grafana_custom_dashboard.yaml)"

