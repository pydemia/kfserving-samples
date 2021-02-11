#!/bin/bash

PROJECT_ID="ds-ai-platform"
SOLVER_NM="airuntime-dns01-solver"
gcloud iam service-accounts create $SOLVER_NM --display-name "$SOLVER_NM"
gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member serviceAccount:$SOLVER_NM@$PROJECT_ID.iam.gserviceaccount.com \
   --role roles/dns.admin

gcloud iam service-accounts keys create key.json \
   --iam-account $SOLVER_NM@$PROJECT_ID.iam.gserviceaccount.com

NAMESPACE="istio-system"
kubectl -n $NAMESPACE create secret generic airuntime-dns01-solver-sa \
   --from-file=key.json