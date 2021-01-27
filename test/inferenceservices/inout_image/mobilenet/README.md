# In-Out Json Format Test: MobileNet

<https://www.tensorflow.org/tfx/serving/api_rest#predict_api>

## Prepare `inferenceservice: mobilenet-fullstack`

```sh
INFERENCE_NS="ifsvc"
# MODEL_NAME="mobilenet-fullstack"  # mobilenet, transformer, explainer
MODEL_NAME="mobilenet-prd"  # predictor
INPUT_PATH="@./input_numpy.json"

# kubectl -n $INFERENCE_NS delete -f mobilenet-fullstack.yaml
# kubectl -n $INFERENCE_NS apply -f mobilenet-fullstack.yaml
kubectl -n $INFERENCE_NS apply -f mobilenet-predictor.yaml

echo `kubectl -n $INFERENCE_NS wait \
    --for=condition=ready --timeout=120s\
    inferenceservice $MODEL_NAME`
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "
CLUSTER_IP: $CLUSTER_IP
HOSTNAME  : $SERVICE_HOSTNAME"

```

```sh

INFERENCE_NS="ifsvc"
# MODEL_NAME="mobilenet-fullstack"  # mobilenet, transformer, explainer
MODEL_NAME="mobilenet-prd"  # predictor
INPUT_PATH="@./input_numpy.json"

# kubectl -n $INFERENCE_NS delete -f mobilenet-fullstack.yaml
# kubectl -n $INFERENCE_NS apply -f mobilenet-fullstack.yaml

echo `kubectl -n $INFERENCE_NS wait \
    --for=condition=ready --timeout=120s\
    inferenceservice $MODEL_NAME`
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
SERVICE_HOSTNAME=$(kubectl -n $INFERENCE_NS get inferenceservice $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo "
CLUSTER_IP: $CLUSTER_IP
HOSTNAME  : $SERVICE_HOSTNAME"

# PREDICTION
curl -v -H "Host: ${SERVICE_HOSTNAME}" \
  http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict \
  -d $INPUT_PATH > ./logs/output_predict.json

echo "
Predict Log: ./logs/output_predict.json"

# EXPLANATION
# BUG: env_var not working
curl -v \
  --max-time 600 \
  --connect-timeout 600 \
  -H "Host: ${SERVICE_HOSTNAME}" \
  http://104.198.233.27/v1/models/mobilenet-fullstack:explain \
  -d $INPUT_PATH > ./logs/output_explain.json
echo "
Explain Log: ./logs/output_explain.json"
```

## Create inputs
```sh
# Basic: {instances: [elephant_img_numpy]}
python mobilenet_input_builder.py \
    --input elephant.jpg \
    --output input_numpy.json \
    --output_type numpy

# Tensorname: {instances: [{"input_1": elephant_img_numpy}]}
python mobilenet_input_builder.py \
    --input elephant.jpg \
    --input_tensorname 'input_1' \
    --output input_numpy_tensorname.json \
    --output_type numpy


# Batch Input(A input with 2 images): {"instances": [elephant_img_numpy,squirrel_img_numpy]}
python mobilenet_input_builder.py \
    --input elephant.jpg,squirrel.jpg \
    --output input_numpy_multi_images.json \
    --output_type numpy


# Batch Input, Tensorname(A input with 2 images): {"instances": [{"input_1": elephant_img_numpy},{"input_1",squirrel_img_numpy}]}
python mobilenet_input_builder.py \
    --input elephant.jpg,squirrel.jpg \
    --input_tensorname 'input_1' \
    --output input_numpy_multi_images_tensorname.json \
    --output_type numpy
```

### Describe inputs

```sh
$ saved_model_cli show \
    --dir ../../../inferenceservice/mobilenet/predictor/mobilenet_saved_model/0001 \
    --tag_set serve \
    --signature_def serving_default

The given SavedModel SignatureDef contains the following input(s):
  inputs['input_1'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 224, 224, 3)
      name: serving_default_input_1:0
The given SavedModel SignatureDef contains the following output(s):
  outputs['act_softmax'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 1000)
      name: StatefulPartitionedCall:0
Method name is: tensorflow/serving/predict
```

`input_numpy.json`
```json
{
    "instances": [
        elephant_image_as_numpy
    ]
}
```


`input_numpy_tensorname.json`
```json
{
    "instances": [
        {"input_1": elephant_image_as_numpy}
    ]
}
```

`input_numpy_multi_images.json`
```json
{
    "instances": [
        elephant_image_as_numpy,
        squirrel_image_as_numpy
    ]
}
```


`input_numpy_multi_images_tensorname.json`
```json
{
    "instances": [
        {"input_1": elephant_image_as_numpy},
        {"input_1": squirrel_image_as_numpy}
    ]
}
```

## Get predictions

```sh
$ python test_inference.py \
    --img_url input_numpy.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

Calling  http://104.198.233.27/v1/models/mobilenet-prd:predict
predict: result saved: input_numpy_output.json
```

```sh
$ python test_inference.py \
    --img_url input_numpy_tensorname.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

Calling  http://104.198.233.27/v1/models/mobilenet-prd:predict
predict: result saved: input_numpy_tensorname_output.json
```

```sh
$ python test_inference.py \
    --img_url input_numpy_multi_images.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

Calling  http://104.198.233.27/v1/models/mobilenet-prd:predict
predict: result saved: input_numpy_multi_images_output.json
```

```sh
$ python test_inference.py \
    --img_url input_numpy_multi_images_tensorname.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict

Calling  http://104.198.233.27/v1/models/mobilenet-prd:predict
predict: result saved: input_numpy_multi_images_tensorname_output.json
```

### Output Structure

```json
{
    "predictions" [
        elephant_numpy_output
    ]
}
```


```json
{
    "predictions" [
        elephant_numpy_output
    ]
}
```


```json
{
    "predictions" [
        elephant_numpy_output, squirrel_numpy_output
    ]
}
```


```json
{
    "predictions" [
        elephant_numpy_output, squirrel_numpy_output
    ]
}
```