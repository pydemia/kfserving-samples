# kfserving-samples
KFServing Codes


## Installation

### Setup GKE Cluster

```bash
cd setup/cluster
vim gke-kfserving-<codename>.sh
./gke-kfserving-<codename>.sh  > gke-kfserving-<codename>.log 2>&1
```

### Install k8s Resources

```bash
cd setup/resources/install/kfserving/0.5.0-rc2

./kfserving-installer setup > setup-kfserving.log 2>&1  
./kfserving-installer install > install-kfserving.log 2>&1  
```