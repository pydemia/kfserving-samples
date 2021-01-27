
NODEPOOL_NAME="gpu-k80-nodepool"
CLUSTER="kfserving-dev"
REGION="us-central1"
#ZONE="us-central1-a"
#NODE_LOCATIONS="us-central1-a,us-central1-b,us-central1-f"
NODE_LOCATIONS="us-central1-c" #"us-central1-f"
NODE_TAINTS="nvidia.com/gpu=present:NoSchedule"
#NODE_TAINTS="preemptible=true:NoSchedule"

PROJECT_ID="ds-ai-platform"

ACCELERATOR_TYPE="nvidia-tesla-k80" #"nvidia-tesla-t4"
ACCELERATOR_COUNT="2"
NUM_NODES="2"
MIN_NODES="0"
MAX_NODES="5"

DISK_TYPE="pd-standard"  #  pd-standard, pd-ssd
DISK_SIZE="80GB"  # default: 100GB
IMAGE_TYPE="UBUNTU"  # COS, UBUNTU, COS_CONTAINERD, UBUNTU_CONTAINERD, WINDOWS_SAC, WINDOWS_LTSC (gcloud container get-server-config)
# MACHINE_TYPE="n1-standard-4" # 4CPUs, 15GB (gcloud compute machine-types list) <https://cloud.google.com/compute/vm-instance-pricing>
MACHINE_TYPE="n1-standard-8" # 8CPUs, 30GB 
SERVICE_ACCOUNT="yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com"
MAX_PODS_PER_NODE="110"

WORKLOAD_METADATA="GKE_METADATA"
METADATA="disable-legacy-endpoints=true"
LABELS="cz_owner=youngju_kim,application=kfserving,gpu=t4"
TAGS="yjkim-kube-instance,yjkim-kube-istio,yjkim-kube-knative,yjkim-kube-kafka,yjkim-kube-subnetall"


# UBUNTU
curl -sL https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/ubuntu/daemonset-preloaded.yaml -o ubuntu_daemonset-preloaded.yaml && \
  kubectl apply -f ubuntu_daemonset-preloaded.yaml


####### https://cloud.google.com/kubernetes-engine/docs/how-to/gpus
# gcloud container node-pools create pool-name \
#   --accelerator type=gpu-type,count=amount \
#   --zone compute-zone --cluster cluster-name \
#   [--num-nodes 3 --min-nodes 0 --max-nodes 5 --enable-autoscaling]


    # --node-taints=$NODE_TAINTS \
    # --preemptible \
gcloud container node-pools create $NODEPOOL_NAME \
    --cluster $CLUSTER \
    --accelerator type=$ACCELERATOR_TYPE,count=$ACCELERATOR_COUNT \
    --region $REGION \
    --node-locations $NODE_LOCATIONS \
    --num-nodes $NUM_NODES --min-nodes $MIN_NODES --max-nodes $MAX_NODES \
    --enable-autoscaling \
    --service-account=$SERVICE_ACCOUNT \
    --enable-autorepair \
    --no-enable-autoupgrade \
    --machine-type $MACHINE_TYPE \
    --disk-type $DISK_TYPE \
    --disk-size $DISK_SIZE \
    --image-type $IMAGE_TYPE \
    --workload-metadata $WORKLOAD_METADATA \
    --metadata=$METADATA \
    --max-pods-per-node $MAX_PODS_PER_NODE \
    --node-labels=$LABELS \
    --scopes=$SCOPES \
    --tags=$TAGS

# gcloud container node-pools create preemptible-gpu-t4-nodepool \
#     --preemptible \
#     --cluster $CLUSTER \
#     --node-taints=$NODE_TAINTS \
#     --accelerator type=$ACCELERATOR_TYPE,count=$ACCELERATOR_COUNT \
#     --region $REGION \
#     --node-locations $NODE_LOCATIONS \
#     --num-nodes $NUM_NODES --min-nodes $MIN_NODES --max-nodes $MAX_NODES \
#     --enable-autoscaling \
#     --service-account=$SERVICE_ACCOUNT \
#     --enable-autorepair \
#     --no-enable-autoupgrade \
#     --machine-type $MACHINE_TYPE \
#     --disk-type $DISK_TYPE \
#     --disk-size $DISK_SIZE \
#     --image-type $IMAGE_TYPE \
#     --workload-metadata $WORKLOAD_METADATA \
#     --metadata=$METADATA \
#     --max-pods-per-node $MAX_PODS_PER_NODE \
#     --node-labels=$LABELS \
#     --tags=$TAGS
