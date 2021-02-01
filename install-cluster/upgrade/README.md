# UPGRADE

```bash
ns_list=`kubectl get ns | head -n1 | cut -d ' ' -f 1` && \
for ns in $ns_list; do
  kubectl -n $ns rollout restart deployments
done
```