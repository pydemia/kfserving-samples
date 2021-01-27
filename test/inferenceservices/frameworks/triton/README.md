# Trition Inference Test

## Yaml

```yaml
IF_NAMESPACE=""
kubectl -n $IF_NAMESPACE
apiVersion: "serving.kubeflow.org/v1alpha2"
kind: "InferenceService"
metadata:
  name: "triton-simple-string"
spec:
  default:
    predictor:
      triton:
        storageUri: "gs://kfserving-samples/models/tensorrt"
```

* Input

```json
{
    "instances" [...],
}
```

* Output

```json
{
    "predictions" [...]
}
```

---

* GW Input

```json
{
    "instances" [...],
}
```
GW--> 이 모델 정보 -> kdl -> 무슨 작업을 할지 선택

* Model Output
```json
{
    "predictions" [...]
}
```

* GW Output

```json
{
    "predictions" [...],
    "kdl": 0.1,
    // "msa": 0.12
}
```


kdl > 0.5
