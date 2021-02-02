# Minikube, GCP

## Create a nested virtualization enabled VM

https://cloud.google.com/compute/docs/instances/enable-nested-virtualization-vm-instances

1. Create an VM-enabled BootDisk
```bash
DISK_NM="yjkim-vm-enabled-ubuntu-bootdisk"
ZONE="us-central1-c"
IMG_PJT="ubuntu-os-cloud"
IMG_FAMILY="ubuntu-minimal-2004-lts"
LICENSE="https://compute.googleapis.com/compute/v1/projects/vm-options/global/licenses/enable-vmx"
LABELS="cz_owner=youngju_kim,application=kfserving-minikube"

gcloud compute disks create $DISK_NM \
    --image-project $IMG_PJT \
    --image-family $IMG_FAMILY \
    --zone $ZONE \
    --labels=$LABELS
```

```ascii
Created [https://www.googleapis.com/compute/v1/projects/ds-ai-platform/zones/us-central1-c/disks/yjkim-vm-enabled-ubuntu-bootdisk].
NAME                              ZONE           SIZE_GB  TYPE         STATUS
yjkim-vm-enabled-ubuntu-bootdisk  us-central1-c  10       pd-standard  READY
```

1. Create an Boot Image
```bash
IMG_NM="yjkim-vm-enabled-ubuntu-image"
ZONE="us-central1-c"
IMG_PJT="ubuntu-os-cloud"
IMG_FAMILY="ubuntu-minimal-2004-lts"
LICENSE="https://compute.googleapis.com/compute/v1/projects/vm-options/global/licenses/enable-vmx"
LABELS="cz_owner=youngju_kim,application=kfserving-minikube"

gcloud compute images create $IMG_NM \
    --source-disk $DISK_NM \
    --source-disk-zone $ZONE \
    --licenses $LICENSE \
    --labels=$LABELS

```

```ascii
Created [https://www.googleapis.com/compute/v1/projects/ds-ai-platform/global/images/yjkim-vm-enabled-ubuntu-image].
NAME                           PROJECT         FAMILY  DEPRECATED  STATUS
yjkim-vm-enabled-ubuntu-image  ds-ai-platform                      READY
```

1. Create a VM

```bash
VM_NM="yjkim-kfs-minikube"
PROJECT_ID="ds-ai-platform"
ZONE="us-central1-c"
MACHINE_TYPE="n1-standard-8" # 4CPUs, 32GB (gcloud compute machine-types list) <https://cloud.google.com/compute/vm-instance-pricing>
DISK_TYPE="pd-standard"  #  pd-standard, pd-ssd
DISK_SIZE="100GB"  # default: 100GB
ACCELERATOR="type=nvidia-tesla-k80,count=1"
NETWORK="yjkim-vpc"  # "default" or VPC
SUBNETWORK="yjkim-kube-subnet"
DESCRIPTION="A testbed Kubernetes cluster;for KFServing InferenceService, in minikube"
MIN_CPU_PLATFORM="Intel Haswell"
LABELS="cz_owner=youngju_kim,application=kfserving-minikube"
TAGS="yjkim-kube-instance,yjkim-kube-istio,yjkim-kube-knative,yjkim-kube-kafka,yjkim-kube-subnetall"  # (https://cloud.google.com/compute/docs/labeling-resources), tag1,tag2


#     --accelerator=$ACCELERATOR \
gcloud compute instances create $VM_NM \
    --description=$DESCRIPTION \
    --zone $ZONE \
    --min-cpu-platform $MIN_CPU_PLATFORM \
    --image $IMG_NM \
    --boot-disk-size=$DISK_SIZE \
    --machine-type=$MACHINE_TYPE \
    --network=$NETWORK \
    --subnet=$SUBNETWORK \
    --tags=$TAGS \
    --labels=$LABELS
```

```ascii
WARNING: You have selected a disk size of under [200GB]. This may result in poor I/O performance. For more information, see: https://developers.google.com/compute/docs/disks#performance.
Created [https://www.googleapis.com/compute/v1/projects/ds-ai-platform/zones/us-central1-a/instances/yjkim-kfs-minikube].
WARNING: Some requests generated warnings:
 - Disk size: '100 GB' is larger than image size: '10 GB'. You might need to resize the root repartition manually if the operating system does not support automatic resizing. See https://cloud.google.com/compute/docs/disks/add-persistent-disk#resize_pd for details.

NAME                ZONE           MACHINE_TYPE   PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP   STATUS
yjkim-kfs-minikube  us-central1-a  n1-standard-8               10.128.2.36  34.71.18.104  RUNNING
```

1. Check Nested Virtualization Succeed. The result should be not null.

```bash
$ grep -cw vmx /proc/cpuinfo
8
```

---
In VM:

## Install Kubectl

```bash
curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"

chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
kubectl version --client

# Client Version: version.Info{Major:"1", Minor:"19", GitVersion:"v1.19.0", GitCommit:"e19964183377d0ec2052d1f1fa930c4d7575bd50", GitTreeState:"clean", BuildDate:"2020-08-26T14:30:33Z", GoVersion:"go1.15", Compiler:"gc", Platform:"linux/amd64"}
```

## Install Virtualization Tools(In this case, `kvm2`)

https://help.ubuntu.com/community/KVM/Installation

```bash
sudo apt update
# 18.10 or later
sudo apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
```

## Install Docker

https://docs.docker.com/engine/install/ubuntu/

```bash
# Uninstall the old one & Install the new one
sudo apt-get remove docker docker-engine docker.io containerd runc && \
    sudo apt-get update && \
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
    sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable" && \
    sudo apt-get update && \
    sudo apt-get install -y \
        docker-ce=5:19.03.11~3-0~ubuntu-focal \
        docker-ce-cli=5:19.03.11~3-0~ubuntu-focal \
        containerd.io

sudo systemctl enable docker

# sudo apt list -a docker-ce
```

### (Optional)Rootless Docker deamon

https://docs.docker.com/engine/security/rootless/


### Manage Docker as a Non-root User

https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
sudo chmod 776 /var/run/docker.sock
```

## Install Minikube

```bash
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 \
    && chmod +x minikube && \
    sudo mkdir -p /usr/local/bin/ && \
    sudo install minikube /usr/local/bin/
```

## Start Minikube

As `root`:
```bash
sudo su - 
cd /root && \
    minikube start --driver=none --kubernetes-version v1.15.9

kubectl config current-context
# minikube
```

As a non-root user:
```bash
# sudo mv /root/.kube /root/.minikube $HOME
sudo chown -R $USER $HOME/.kube $HOME/.minikube
```


```ascii
😄  minikube v1.12.3 on Ubuntu 20.04
✨  Using the none driver based on user configuration
👍  Starting control plane node minikube in cluster minikube
🤹  Running on localhost (CPUs=8, Memory=30100MB, Disk=99067MB) ...
ℹ️  OS release is Ubuntu 20.04.1 LTS
🐳  Preparing Kubernetes v1.15.9 on Docker 19.03.11 ...
    ▪ kubelet.resolv-conf=/run/systemd/resolve/resolv.conf
    > kubeadm.sha1: 41 B / 41 B [----------------------------] 100.00% ? p/s 0s
    > kubectl.sha1: 41 B / 41 B [----------------------------] 100.00% ? p/s 0s
    > kubelet.sha1: 41 B / 41 B [----------------------------] 100.00% ? p/s 0s
    > kubectl: 41.00 MiB / 41.00 MiB [--------------] 100.00% 182.82 MiB p/s 0s
    > kubeadm: 38.33 MiB / 38.33 MiB [--------------] 100.00% 158.00 MiB p/s 0s
    > kubelet: 114.16 MiB / 114.16 MiB [------------] 100.00% 106.80 MiB p/s 1s
🤹  Configuring local host environment ...

❗  The 'none' driver is designed for experts who need to integrate with an existing VM
💡  Most users should use the newer 'docker' driver instead, which does not require root!
📘  For more information, see: https://minikube.sigs.k8s.io/docs/reference/drivers/none/

❗  kubectl and minikube configuration will be stored in /root
❗  To use kubectl or minikube commands as your own user, you may need to relocate them. For example, to overwrite your own settings, run:

    ▪ sudo mv /root/.kube /root/.minikube $HOME
    ▪ sudo chown -R $USER $HOME/.kube $HOME/.minikube

💡  This can also be done automatically by setting the env var CHANGE_MINIKUBE_NONE_USER=true
🔎  Verifying Kubernetes components...
🌟  Enabled addons: default-storageclass, storage-provisioner
🏄  Done! kubectl is now configured to use "minikube"

❗  /usr/local/bin/kubectl is version 1.19.0, which may be incompatible with Kubernetes 1.15.9.
💡  You can also use 'minikube kubectl -- get pods' to invoke a matching version
```

#### Case 0: Using `docker`, non-root

```bash
minikube start --driver=docker --kubernetes-version v1.15.9
```


#### Case 1: Non-root user installation
```bash
$ sudo minikube start --driver=none --kubernetes-version v1.15.9

😄  minikube v1.12.3 on Ubuntu 20.04
✨  Using the none driver based on user configuration
👍  Starting control plane node minikube in cluster minikube
🤹  Running on localhost (CPUs=8, Memory=30100MB, Disk=99067MB) ...
ℹ️  OS release is Ubuntu 20.04.1 LTS
🐳  Preparing Kubernetes v1.15.9 on Docker 19.03.11 ...
    ▪ kubelet.resolv-conf=/run/systemd/resolve/resolv.conf
🤹  Configuring local host environment ...

❗  The 'none' driver is designed for experts who need to integrate with an existing VM
💡  Most users should use the newer 'docker' driver instead, which does not require root!
📘  For more information, see: https://minikube.sigs.k8s.io/docs/reference/drivers/none/

❗  kubectl and minikube configuration will be stored in /root
❗  To use kubectl or minikube commands as your own user, you may need to relocate them. For example, to overwrite your own settings, run:

    ▪ sudo mv /root/.kube /root/.minikube $HOME
    ▪ sudo chown -R $USER $HOME/.kube $HOME/.minikube

💡  This can also be done automatically by setting the env var CHANGE_MINIKUBE_NONE_USER=true
🔎  Verifying Kubernetes components...
🌟  Enabled addons: default-storageclass, storage-provisioner
🏄  Done! kubectl is now configured to use "minikube"

❗  /usr/local/bin/kubectl is version 1.19.0, which may be incompatible with Kubernetes 1.15.9.
💡  You can also use 'minikube kubectl -- get pods' to invoke a matching version
```

##### Case 2: `kubernetes=1.18.3` needs ROOT PATH(`/root`).

```bash
$ minikube start --driver=none
😄  minikube v1.12.3 on Ubuntu 20.04
✨  Using the none driver based on user configuration
💣  Sorry, Kubernetes 1.18.3 requires conntrack to be installed in root's path
```

##### Case 3: `KVM2` needs ROOT PRIVILEGE.

```bash
$ sudo minikube start --driver=kvm2 --kubernetes-version v1.15.9

😄  minikube v1.12.3 on Ubuntu 20.04
✨  Using the kvm2 driver based on user configuration
🛑  The "kvm2" driver should not be used with root privileges.
💡  If you are running minikube within a VM, consider using --driver=none:
📘    https://minikube.sigs.k8s.io/docs/reference/drivers/none/
```

### Verify Minikube

```bash
$ minikube status

minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

```bash
$ kubectl config current-context

minikube
```

```bash
minikube update-context
```

---
