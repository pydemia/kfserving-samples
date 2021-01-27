# GPU Prerequisites (GKE)

## Add Nodepool

```sh
# gcloud container node-pools create [POOL_NAME] \
#     --accelerator type=[GPU_TYPE],count=[AMOUNT] --zone [COMPUTE_ZONE] \
#     --cluster [CLUSTER_NAME] [--num-nodes 3 --min-nodes 0 --max-nodes 5 \
#     --enable-autoscaling]
TAGS="yjkim-kube-instance,yjkim-kube-istio,yjkim-kube-knative,yjkim-kube-kafka,yjkim-kube-subnetall"

$ gcloud container node-pools create preemptible-gpu-t4-nodepool \
    --accelerator type=nvidia-tesla-t4,count=1 \
    --region us-central1 \
    --node-locations us-central1-a,us-central1-b,us-central1-f \
    --node-taints=nvidia.com/gpu=present:NoSchedule,preemptible=true:NoSchedule
    --cluster kfserving-dev --num-nodes 2 --min-nodes 0 --max-nodes 5 \
    --enable-autoscaling \
    --preemptible \
    --enable-autorepair \
    --no-enable-autoupgrade \
    --machine-type 
    --disk-type pd-standard \
    --tags=$TAGS

```

:bulb:**Note**: If a GPU node pool is added to a cluster where all the existing node pools are GPU node pools, or if you are creating a new cluster with a GPU attached default pool, the above taint will not be added to the GPU nodes. The taint will also not be added to the existing GPU nodes retrospectively when a non-GPU node pool is added afterwards.

## Install NVIDIA Device Drivers

Google-Provided Daemonset for auto-installation the drivers.
<https://github.com/GoogleCloudPlatform/container-engine-accelerators/tree/stable>

```sh
# COS
curl -sL https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml -o cos_daemonset-preloaded.yaml
kubectl apply -f cos_daemonset-preloaded.yaml

# UBUNTU
curl -sL https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/ubuntu/daemonset-preloaded.yaml -o ubuntu_daemonset-preloaded.yaml
kubectl apply -f ubuntu_daemonset-preloaded.yaml
```

### GPU Node Taints

#### GKE

When you add a GPU node pool to an existing cluster that already runs a non-GPU node pool, GKE automatically taints the GPU nodes with the following node taint:

```ascii
Key: nvidia.com/gpu
Effect: NoSchedule
```

GKE will automatically apply corresponding tolerations to Pods requesting GPUs by running the ExtendedResourceToleration admission controller.

### Specifying GPU type

#### GKE

Apply the GKE Accelerator annotation as follows:

```yaml
metadata:
  annotations:
    "serving.kubeflow.org/gke-accelerator": "nvidia-tesla-t4"
```

## Install GPU in `minikube`

https://minikube.sigs.k8s.io/docs/tutorials/nvidia_gpu/

```sh

