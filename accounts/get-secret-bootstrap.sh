#!/bin/bash

set -e

#account_name="airuntime"
#read -p "Enter serviceaccount [$account_name]: " name
#sa_name=${name:-$account_name}

#namespace="airuntime-system"
#read -p "Enter namespace [$namespace]: " ns
#namespace=${ns:-$namespace}

cluster_name="$(kubectl config current-context)"
cluster_desc="$(kubectl cluster-info|grep 'Kubernetes master')"
cluster_master_ip="$(kubectl cluster-info|grep 'Kubernetes master'| grep -E -o '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')"
sa_name="airuntime"
namespace="airuntime-system"

secret_name="$(kubectl -n $namespace get sa $sa_name -o jsonpath='{.secrets[0].name}')"
decoded_token="$(kubectl -n $namespace get secret $secret_name -o jsonpath='{.data.token}' | base64 -d)"

echo -e "\ntoken for '$namespace/$sa_name':\n$decoded_token
"

filepath="./bootstrap.yml"
#read -p "Enter config-file-path [$filepath]: " fpath
#filepath=${fpath:-$filepath}


template="k8s:
  cluster:
    name: $cluster_name
    master_ip: $cluster_master_ip
  serviceAccount:
    name: $sa_name
    namespace: $namespace
  SAToken: $decoded_token
"

echo -e "$template" > $filepath

echo "token configured."