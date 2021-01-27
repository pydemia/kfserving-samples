echo "'oneshot-install' has been started..." && \
start_tm=`date "+%Y%m%d-%H%M%S"` && \
echo "$start_tm" && \
cd install-cluster && \
cd kfserving-0.3.0 && \
./create-gke-kfserving-devel.sh && \
echo "cluster created" && \
./install_kfserving.sh > install.log && \
echo "kfserving installed" && \
cd .. && \
cd troubleshooting && \
kubectl apply -f knative-v0.14.0-monitoring-metrics-prometheus-upscale-limit.yaml && \
echo "knative-prometheus upscaled" && \
cd .. && \
cd dashboard && \
istioctl manifest apply \
  --set values.prometheus.enabled=true \
  --set values.grafana.enabled=true \
  --set values.kiali.enabled=true \
  --set "values.kiali.dashboard.grafanaURL=http://grafana:3000" \
  --set values.tracing.enabled=true && \
./expose-istio-dashboard.sh && \
echo "istio-monitoring exposed" && \
cd .. && \
echo "'oneshot-install' has been finished." && \
end_tm=`date "+%Y%m%d-%H%M%S"` && \
echo "$start_tm -> $end_tm" > oneshot-install.log
