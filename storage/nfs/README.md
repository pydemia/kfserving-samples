# NFS

## `nfs-client-provisioner`

```bash
helm install nfs-client-provisioner \
    --namespace=default \
    --set nfs.server=61.97.6.153 \
    --set nfs.path=/pacs/input \
    --set storageClass.name=nfs \
    --set storageClass.defaultClass=true \
    --set serviceAccount.name=nfs-manager \
    stable/nfs-client-provisioner

helm delete nfs-client-provisioner2

helm template nfs-client-provisioner \
    --namespace=default \
    --set nfs.server=61.97.6.153 \
    --set nfs.path=/pacs/input \
    --set storageClass.name=nfs \
    --set storageClass.defaultClass=true \
    --set serviceAccount.name=nfs-manager \
    stable/nfs-client-provisioner \
> ./nfs-client-privisioner.yaml

kubectl apply -f ./nfs-client-privisioner.yaml

kubectl delete -f ./nfs-client-privisioner.yaml


helm install stable/nfs-client-provisioner --name nfs-cp --set nfs.server=${FSADDR} --set nfs.path=/volumes
watch kubectl get po -l app=nfs-client-provisioner

helm install --name postgresql --set persistence.storageClass=nfs-client stable/postgresql
watch kubectl get po -l app=postgresql
```

```json
[{"op": "replace", "path": "/spec/template/spec/containers/resources", "value":{"limits":{"memory": "3000Mi"},"requests": {"memory": "1000Mi"}}}]

```