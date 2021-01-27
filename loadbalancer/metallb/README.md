# Baremetal LoadBalancer: `MetalLB`

## Installation


```bash
kubectl apply -f https://raw.githubusercontent.com/google/metallb/v0.7.3/manifests/metallb.yaml

$ kubectl get pods -n metallb-system

```

## ConfigMap

```bash

kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - 192.168.56.240-192.168.56.250
EOF
```

```bash
kubectl logs -l component=speaker -n metallb-system
```