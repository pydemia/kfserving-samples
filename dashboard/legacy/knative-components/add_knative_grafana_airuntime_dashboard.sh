
DASHBOARD_NAME="airuntime-total-dashboard"
read -p "Enter Dashboard Name [$DASHBOARD_NAME]: " name
DASHBOARD_NAME=${name:-$DASHBOARD_NAME}

KUBECTL_COMMAND="kubectl --insecure-skip-tls-verify"

$KUBECTL_COMMAND apply -f ${DASHBOARD_NAME}.yaml

ADD_TEMPLATE="[
    {
        "op": "add",
        "path": "/spec/template/spec/containers/0/volumeMounts/-",
        "value": {
            "name": "${DASHBOARD_NAME}",
            "mountPath": "/grafana-dashboard-definition/${DASHBOARD_NAME}"
        }
    },
    {
        "op": "add",
        "path": "/spec/template/spec/volumes/-",
        "value": {
            "name": "${DASHBOARD_NAME}",
            "configMap": {"name": "${DASHBOARD_NAME}"}
        }
    }
]"

$KUBECTL_COMMAND -n knative-monitoring patch deployments grafana --type=json -p="${ADD_TEMPLATE}"

# $KUBECTL_COMMAND -n knative-monitoring patch configmap grafana-dashboards --type=merge --patch "$(cat patch_grafana_custom_dashboard.yaml)"


# configmap_patch_str="
#     - name: "${DASHBOARD_NAME}"
#       org_id: 1
#       folder: ''
#       type: file
#       options:
#         path: /grafana-dashboard-definition/${DASHBOARD_NAME}
# "

configmap_patch_str="
- name: '${DASHBOARD_NAME}'
  org_id: 1
  folder: ''
  type: file
  options:
    path: /grafana-dashboard-definition/${DASHBOARD_NAME}"


# echo "$(cat patch_grafana_custom_dashboard.yaml) $configmap_patch_str"
base_template="data:
  dashboards.yaml: |
"
old_list="$($KUBECTL_COMMAND -n knative-monitoring get configmap  grafana-dashboards -o jsonpath='{.data.dashboards\.yaml}')"
echo "$old_list" > old_list.txt
# new_list="$(echo "$(echo "$old_list") $configmap_patch_str")"
# new_list="echo $base_template <(echo) "$old_list" <(echo) "$configmap_patch_str""
new_list="$(echo "$base_template""$(echo "$old_list"|sed 's/^/    /')""$(echo "$configmap_patch_str"|sed 's/^/    /')")"


$KUBECTL_COMMAND -n knative-monitoring patch configmap grafana-dashboards --type=merge --patch "$(echo "$new_list")"
echo "$new_list" > ${DASHBOARD_NAME}-patch.yaml
# $KUBECTL_COMMAND -n knative-monitoring patch configmap grafana-dashboards --type=yaml --patch  ${DASHBOARD_NAME}-patch.yaml

$KUBECTL_COMMAND -n knative-monitoring rollout restart deployment grafana
