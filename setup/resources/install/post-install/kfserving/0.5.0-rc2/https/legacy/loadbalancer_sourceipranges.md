```yml
spec:
  loadBalancerSourceRanges:
  - 220.78.30.93/32
  - 211.45.60.5/32
  - 10.128.1.3/32
```


```bash
DASHBOARD_NAME=${name:-$DASHBOARD_NAME}

KUBECTL_COMMAND="kubectl --insecure-skip-tls-verify"

ADD_TEMPLATE="[
    {
        "op": "add",
        "path": "/spec/loadBalancerSourceRanges/-",
        "value": "220.78.30.93/32"
    },
    {
        "op": "add",
        "path": "/spec/loadBalancerSourceRanges/-",
        "value": "211.45.60.5/32"
    },
    {
        "op": "add",
        "path": "/spec/loadBalancerSourceRanges/-",
        "value": "10.128.1.3/32"
    }
]"

$KUBECTL_COMMAND -n istio-system patch svc istio-ingressgateway --type=json -p="${ADD_TEMPLATE}"
```
