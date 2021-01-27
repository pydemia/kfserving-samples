# Helm

## Installation

### Check a `kubernetes` cluster exists
```sh
kubectl config current-context
```

### Download `helm`
```sh
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
```

### Create `tiller` service account and assign cluster-admin role, then initiate `helm` & install `tiller`

```sh
kubectl -n kube-system create sa tiller
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account tiller --history-max 200
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'
```

### Update Chart list

```sh
helm repo update
```

### Get available list
```sh
helm search
helm search mysql
```

### Deploy via `helm`
```sh
helm inspect stable/mariadb
helm install stable/mariadb --name my-maria
helm status my-maria
```

### Customize config

```sh
helm inspect values stable/mariadb

echo '{mariadbUser: user0, mariadbDatabase: user0db}' > config.yaml
helm install -f config.yaml stable/mariadb
```

### Upgrade config

```sh
helm upgrade -f panda.yaml happy-panda stable/mariadb
helm get values happy-panda
helm rollback happy-panda 1
```

Get all:
```sh
curl -fsSL https://get.helm.sh/helm-v2.16.7-linux-amd64.tar.gz | tar -zxvf - && \
mkdir -p $HOME/.local/bin && \
mv linux-amd64/helm $HOME/.local/bin && \
mv linux-amd64/tiller $HOME/.local/bin/ && \
rm -r linux-amd64
```


Get `helm` only:
```sh
curl -fsSL https://get.helm.sh/helm-v2.16.7-linux-amd64.tar.gz | tar -zxvf - --strip-components 1 linux-amd64/helm
mkdir -p $HOME/.local/bin
mv ./helm $HOME/.local/bin/
```
