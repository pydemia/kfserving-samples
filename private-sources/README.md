
# Set Private

## Create secret keys

### Docker Hub

```sh
$ docker login
Authenticating with existing credentials...
WARNING! Your password will be stored unencrypted in xxxxx/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded

$ cat xxxxx/config.json |grep "https://index.docker.io/v1/"

"https://index.docker.io/v1/": {
                        "auth": "xxxxxxxxxxxxx"
                },

$ kubectl create secret generic regcred \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson

# $ kubectl create secret docker-registry regcred \
#     --docker-server=docker.io \
#     --docker-username=<your-name> \
#     --docker-password=<your-pword> \
#     --docker-email=<your-email>

$ OWNER_NAME="pydemia" && \
  OWNER_MAIL="pydemia@gmail.com" && \
  INFERENCE_NS="ifsvc" && \
  kubectl -n $INFERENCE_NS create secret docker-registry \
    $OWNER_NAME-docker-private-key \
    --docker-server=docker.io \
    --docker-username=$OWNER_NAME \
    --docker-email=$OWNER_MAIL \
    --docker-password=<password>

secret/pydemia-docker-private-key created
```

### GCP

```sh
$ gcloud iam service-accounts keys create gcloud-application-credentials.json \
    --iam-account yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com
```


```sh
# $ kubectl create secret generic gcs-private-key \
#     --from-file=gcloud-application-credentials.json=xxxx-4129b72eaa4a.json
# secret/gcs-private-sa created

$ OWNER_NAME="yjkim-kube-admin-sa" && \
  INFERENCE_NS="ifsvc" && \
  kubectl -n $INFERENCE_NS create secret generic \
    $OWNER_NAME-gcs-private-key \
    --from-file=gcloud-application-credentials.json=xxxx-4129b72eaa4a.json
secret/yjkim-kube-admin-sa-gcs-private-key created
```


```sh
$ INFERENCE_NS="pavin"
SA_NAME="default"
OWNER_NAME="yjkim-kube-admin-sa"
GCR_KEY=$OWNER_NAME-gcr-private-key


# Setup registry credentials so we can pull images from gcr
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://gcr.io

kubectl create secret generic $GCR_KEY \
    --namespace=$INFERENCE_NS \
    --from-file=.dockerconfigjson="${HOME}/.docker/config.json" \
    --type=kubernetes.io/dockerconfigjson \
    --output yaml --dry-run | kubectl apply -f - # create or update if already created

secret/yjkim-kube-admin-sa-gcr-private-key created
```

```sh
# $ kubectl patch sa default \
#     -p '{"imagePullSecrets": [{"name": "gcr-private-key"}]}'
# serviceaccount/default patched
```


### AWS

<https://github.com/kubeflow/kfserving/tree/master/docs/samples/s3>
<https://www.kubeflow.org/docs/aws/aws-e2e/>


`s3-private-key.yaml`
```sh
apiVersion: v1
kind: Secret
metadata:
  name: s3-private-key
  annotations:
       annotations:
     serving.kubeflow.org/s3-endpoint: s3.us-east-1.amazonaws.com # replace with your s3 endpoint
     serving.kubeflow.org/s3-region: us-east-1
     serving.kubeflow.org/s3-usehttps: "1" # by default 1, for testing with minio you need to set to 0
     serving.kubeflow.org/s3-verifyssl: "1" # by default 1, for testing with minio you need to set to 0
type: Opaque
data:
  awsAccessKeyID: xxxxxxxxxx
  awsSecretAccessKey: xxxxxxxxx

```

```sh
$ INFERENCE_NS="ifsvc" && \
  kubectl -n $INFERENCE_NS apply -f yjkim1-s3-private-key.yaml

secret/yjkim1-s3-private-key created
```

---

## Create `ServiceAccount`


```yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: yjkim-private-deployer-s3
  namespace: ifsvc
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: yjkim-private-deployer-gs
  namespace: ifsvc
EOF
#serviceaccount/yjkim-private-deployer-s3 created
#serviceaccount/yjkim-private-deployer-gs created
```

---

## Patch `secrets` to `ServiceAccount`

:warning: You **CANNOT** use multiple `STORAGE_KEY` to one `ServiceAccout`!
You should have multiple `ServiceAccount` for each storage account source as `storageUri`.

```sh
GCS_KEY="yjkim-kube-admin-sa-gcs-private-key"
S3_KEY="yjkim1-s3-private-key"

$ SA_NAME="yjkim-private-deployer-s3" && \
  STORAGE_KEY=$S3_KEY && \
  GCR_KEY="yjkim-kube-admin-sa-gcr-private-key" && \
  DOCKER_HUB_KEY="pydemia-docker-private-key" && \
  kubectl -n $INFERENCE_NS patch sa $SA_NAME \
    -p "{\"secrets\":[{\"name\": \"$STORAGE_KEY\"}],\"imagePullSecrets\": [{\"name\": \"$GCR_KEY\"},{\"name\": \"$DOCKER_HUB_KEY\"}]}"

$ SA_NAME="yjkim-private-deployer-gs" && \
  STORAGE_KEY=$GCS_KEY && \
  GCR_KEY="yjkim-kube-admin-sa-gcr-private-key" && \
  DOCKER_HUB_KEY="pydemia-docker-private-key" && \
  kubectl -n $INFERENCE_NS patch sa $SA_NAME \
    -p "{\"secrets\":[{\"name\": \"$STORAGE_KEY\"}],\"imagePullSecrets\": [{\"name\": \"$GCR_KEY\"},{\"name\": \"$DOCKER_HUB_KEY\"}]}"

serviceaccount/pydemia-private-deployer patched


# $ kubectl -n inference-test patch sa gcs-private-sa \
#     -p '{"secrets":[{"name": "gcs-private-key"},{"name": "gcs-private-sa-token-qhx6w"}],"imagePullSecrets": [{"name": "gcr-private-key"}]}'
```

```yaml
$ kubectl -n $INFERENCE_NS get sa $SA_NAME -o yaml

apiVersion: v1
imagePullSecrets:
- name: yjkim-kube-admin-sa-gcr-private-key
- name: pydemia-docker-private-key
kind: ServiceAccount
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"annotations":{},"name":"pydemia-private-deployer","namespace":"ifsvc"}}
  creationTimestamp: "2020-05-27T02:24:51Z"
  name: pydemia-private-deployer
  namespace: ifsvc
  resourceVersion: "254411"
  selfLink: /api/v1/namespaces/ifsvc/serviceaccounts/pydemia-private-deployer
  uid: 62d7a5a5-2fcc-4032-ad0e-9ff6c4aeb031
secrets:
- name: yjkim1-s3-private-key
- name: pydemia-private-deployer-token-nbq6q

```
