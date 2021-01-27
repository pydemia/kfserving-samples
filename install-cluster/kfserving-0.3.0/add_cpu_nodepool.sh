
CLUSTER="kfserving-devel"
REGION="us-central1"
#ZONE="us-central1-a"
NODE_LOCATIONS="us-central1-a,us-central1-b,us-central1-f"
# NODE_LOCATIONS="us-central1-f"
#NODE_TAINTS="nvidia.com/gpu=present:NoSchedule"
#NODE_TAINTS="preemptible=true:NoSchedule"


NUM_NODES="2"
MIN_NODES="0"
MAX_NODES="4"


DISK_TYPE="pd-standard"  #  pd-standard, pd-ssd
DISK_SIZE="100GB"  # default: 100GB
IMAGE_TYPE="UBUNTU"  # COS, UBUNTU, COS_CONTAINERD, UBUNTU_CONTAINERD, WINDOWS_SAC, WINDOWS_LTSC (gcloud container get-server-config)
# MACHINE_TYPE="n1-standard-4" # 4CPUs, 15GB (gcloud compute machine-types list) <https://cloud.google.com/compute/vm-instance-pricing>
MACHINE_TYPE="n1-standard-8" # 8CPUs, 30GB 
SERVICE_ACCOUNT="yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com"
MAX_PODS_PER_NODE="110"

WORKLOAD_METADATA="GKE_METADATA"
METADATA="disable-legacy-endpoints=true"
LABELS="cz_owner=youngju_kim,application=kfserving"
TAGS="yjkim-kube-instance,yjkim-kube-istio,yjkim-kube-knative,yjkim-kube-kafka,yjkim-kube-subnetall"
SCOPES="gke-default,pubsub,compute-rw,storage-full,trace,monitoring-write"


gcloud container node-pools create cpu-nodepool \
    --cluster $CLUSTER \
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
