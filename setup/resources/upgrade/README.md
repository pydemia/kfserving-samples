# UPGRADE

```bash
ns_list=`kubectl get ns -o jsonpath="{.items[*].metadata.name}"`
for ns in $ns_list; do
  kubectl -n $ns rollout restart deployments
done
```

```zsh
ns_list=`kubectl get ns -o jsonpath="{.items[*].metadata.name}"`
for ns in $( echo $ns_list ); do
  kubectl -n $ns rollout restart deployments
done
```