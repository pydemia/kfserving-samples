# Known Issues when Update an existing cluster

```bash
✔ Istio core installed
✔ Istiod installed
✔ Ingress gateways installed
✔ Addons installed
✔ Installation complete
Error from server (Invalid): error when applying patch:
{"metadata":{"annotations":{"kubectl.kubernetes.io/last-applied-configuration":"{\"apiVersion\":\"v1\",\"kind\":\"Service\",\"metadata\":{\"annotations\":{},\"labels\":{\"app\":\"grafana\",\"serving.knative.dev/release\":\"v0.15.0\"},\"name\":\"grafana\",\"namespace\":\"knative-monitoring\"},\"spec\":{\"ports\":[{\"port\":30802,\"protocol\":\"TCP\",\"targetPort\":3000}],\"selector\":{\"app\":\"grafana\"}}}\n"},"labels":{"serving.knative.dev/release":"v0.15.0"}},"spec":{"type":null}}
to:
Resource: "/v1, Resource=services", GroupVersionKind: "/v1, Kind=Service"
Name: "grafana", Namespace: "knative-monitoring"
for: "knative-0.15.0/monitoring-metrics-prometheus.yaml": Service "grafana" is invalid: spec.ports[0].nodePort: Forbidden: may not be used when `type` is 'ClusterIP'
Error from server (Invalid): error when applying patch:
{"metadata":{"annotations":{"kubectl.kubernetes.io/last-applied-configuration":"{\"apiVersion\":\"v1\",\"kind\":\"Service\",\"metadata\":{\"annotations\":{},\"labels\":{\"serving.knative.dev/release\":\"v0.15.0\"},\"name\":\"prometheus-system-np\",\"namespace\":\"knative-monitoring\"},\"spec\":{\"ports\":[{\"port\":8080,\"targetPort\":9090}],\"selector\":{\"app\":\"prometheus\"}}}\n"},"labels":{"serving.knative.dev/release":"v0.15.0"}},"spec":{"type":null}}
to:
Resource: "/v1, Resource=services", GroupVersionKind: "/v1, Kind=Service"
Name: "prometheus-system-np", Namespace: "knative-monitoring"
for: "knative-0.15.0/monitoring-metrics-prometheus.yaml": Service "prometheus-system-np" is invalid: spec.ports[0].nodePort: Forbidden: may not be used when `type` is 'ClusterIP'
```


