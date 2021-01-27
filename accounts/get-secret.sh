#!/bin/bash

set -e

account_name="airuntime"
read -p "Enter serviceaccount [$account_name]: " name
sa_name=${name:-$account_name}

namespace="airuntime-system"
read -p "Enter namespace [$namespace]: " ns
namespace=${ns:-$namespace}

secret_name="$(kubectl -n $namespace get sa $sa_name -o jsonpath='{.secrets[0].name}')"
decoded_token="$(kubectl -n $namespace get secret $secret_name -o jsonpath='{.data.token}' | base64 -d)"

echo -e "\ntoken for '$namespace/$sa_name':\n$decoded_token
"

filepath="/data/airuntime/config/common.yml"
read -p "Enter config-file-path [$filepath]: " fpath
filepath=${fpath:-$filepath}

sed -i "s/^  SAToken:\(.*\)/  SAToken: $decoded_token/" $filepath
