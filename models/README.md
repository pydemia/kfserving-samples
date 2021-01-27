# Hemorrhage

## Build Environment via Docker

```sh
./build_docker

docker run --rm -it \
    --workdir /tf/seg_test \
    --mount src="$(pwd)",target=/tmp,type=bind \
    -p 8988:8888/tcp \
    gcr.io/ds-ai-platform/hemorrhage:v0.1.0
```

Inside docker:
```sh
$ python get_savedmodel.py 

2020-06-02 17:58:33.000057: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcuda.so.1
2020-06-02 17:58:33.000079: E tensorflow/stream_executor/cuda/cuda_driver.cc:318] failed call to cuInit: UNKNOWN ERROR (-1)
2020-06-02 17:58:33.000093: I tensorflow/stream_executor/cuda/cuda_diagnostics.cc:156] kernel driver does not appear to be running on this host (758aa8ff8582): /proc/driver/nvidia/version does not exist
2020-06-02 17:58:33.000264: I tensorflow/core/platform/cpu_feature_guard.cc:142] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
2020-06-02 17:58:33.004373: I tensorflow/core/platform/profile_utils/cpu_utils.cc:94] CPU Frequency: 4007900000 Hz
2020-06-02 17:58:33.004616: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x41c8260 initialized for platform Host (this does not guarantee that XLA will be used). Devices:
2020-06-02 17:58:33.004627: I tensorflow/compiler/xla/service/service.cc:176]   StreamExecutor device (0): Host, Default Version
WARNING:tensorflow:From /usr/local/lib/python3.6/dist-packages/tensorflow_core/python/ops/resource_variable_ops.py:1630: calling BaseResourceVariable.__init__ (from tensorflow.python.ops.resource_variable_ops) with constraint is deprecated and will be removed in a future version.
Instructions for updating:
If using Keras pass *_constraint arguments to layers.
2020-06-02 17:58:48.010895: W tensorflow/python/util/util.cc:299] Sets are not currently considered sequences, but this may change in the future, so consider avoiding using them
```

```sh
$ ./clean_cache_and_show_savedmodel.sh

The given SavedModel SignatureDef contains the following input(s):
  inputs['input'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 512, 512, 1)
      name: serving_default_input:0
The given SavedModel SignatureDef contains the following output(s):
  outputs['tf_op_layer_resize_2/ResizeBilinear'] tensor_info:
      dtype: DT_FLOAT
      shape: (-1, 512, 512, 2)
      name: StatefulPartitionedCall:0
Method name is: tensorflow/serving/predict
```

```sh
gsutil -m cp -r ./saved_model/ gs://yjkim-models/kfserving/hemorrhage/saved_model/0001
aws s3 cp --recursive ./saved_model s3://yjkim-models/kfserving/hemorrhage/saved_model/0001
```