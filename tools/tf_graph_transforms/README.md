# Tensorflow Graph Tools

<https://github.com/tensorflow/tensorflow/tree/master/tensorflow/tools/graph_transforms>

* `saved_model_cli`
```sh
saved_model_cli \
  show \
  --dir /tmp/saved_model \
  --tag_set serve \
  --signature_def serving_default

benchmark_model \
  --graph=/tmp/saved_model/saved_model.pb \
  --input_layer="serving_default_input" \
  --input_layer_shape="1,512,512,1" \
  --input_layer_type="float" \
  --output_layer="StatefulPartitionedCall" \
  --show_flops

```


* `freeze_graph`

```sh
freeze_graph \
  --input_binary=true \
  --input_saved_model_dir=/tmp/saved_model \
  --saved_model_tags=serve \
  --clear_devices=true \
  --output_graph=/tmp/saved_model/saved_model_frozen.pb \
  --output_node_names="StatefulPartitionedCall"

```

* `transform_graph`

```sh
transform_graph \
  --in_graph=/tmp/saved_model/saved_model_frozen.pb \
  --out_graph=/tmp/saved_model/saved_model_transformed.pb \
  --inputs='input' \
  --outputs='StatefulPartitionedCall' \
  --transforms='
    strip_unused_nodes(type=float, shape="1,512,512,1")
    remove_nodes(op=Identity, op=CheckNumerics)
    fold_constants(ignore_errors=true)
    fold_batch_norms
    fold_old_batch_norms
    quantize_weights'
```

* `summarize_graph`
```sh
summarize_graph \
  --in_graph=/tmp/saved_model/saved_model_frozen.pb

summarize_graph \
  --in_graph=/tmp/saved_model/saved_model_transformed.pb
```

* `benchmark_model`
```sh
cd /tensorflow
bazel run tensorflow/tools/benchmark:benchmark_model -- --graph=/tmp/saved_model/saved_model_frozen.pb --show_flops --input_layer=serving_default_input --input_layer_type=float --input_layer_shape=-1,512,512,1 --output_layer=StatefulPartitionedCall

benchmark_model \
  --graph=/tmp/saved_model/saved_model_frozen.pb \
  --input_layer="serving_default_input:0" \
  --input_layer_shape="1,512,512,1" \
  --input_layer_type="float" \
  --output_layer="StatefulPartitionedCall:0" \
  --show_flops

benchmark_model \
  --graph=/tmp/saved_model/saved_model_transformed.pb \
  --input_layer="serving_default_input:0" \
  --input_layer_shape="1,512,512,1" \
  --input_layer_type="float" \
  --output_layer="StatefulPartitionedCall:0" \
  --show_flops
```



:warning: 
* <https://github.com/tensorflow/tensorflow/issues/22957>
* <https://stackoverflow.com/questions/51858203/cant-import-frozen-graph-with-batchnorm-layer>
```py
import tensorflow as tf
tf.keras.backend.clear_session()
tf.keras.backend.set_learning_phase(0)
# K.clear_session()
# K.set_learning_phase(0)
```
> as @ardianumam mentions, you need to set your keras to inference mode before loading or constructing your model. TFTRT works with frozen models but unless keras learning phase it set to inference mode graph partially stays in training mode. @fferroni as logs mention, your device is running out of memory. @anilsathyan7 @pkubik are these errors happen when you try to accelerate your models with TFTRT or when you load your keras models. If they are not happening on the graphs produced by TFTRT conversion please open a separate issue.

* `optimize_for_inference`
```sh

optimize_for_inference \
  --input=/tmp/saved_model/saved_model_frozen.pb \
  --output=/tmp/saved_model/saved_model_optimized.pb \
  --frozen_graph=True \
  --input_names="serving_default_input" \
  --output_names="StatefulPartitionedCall"

summarize_graph \
  --in_graph=/tmp/saved_model/saved_model_optimized.pb


benchmark_model \
  --graph=/tmp/saved_model/saved_model_optimized.pb \
  --input_layer="serving_default_input:0" \
  --input_layer_shape="1,512,512,1" \
  --input_layer_type="float" \
  --output_layer="StatefulPartitionedCall:0" \
  --show_flops
```


This reduces *Inference times*, as well as *Model size*.

* `saved_model.pb`: `4MB(Graph) + 17+1(Variables)`
* `saved_model_frozen.pb`: `20MB(Graph+Variables-Const)`
* `saved_model_optimized.pb`: `17MB(Graph+Variables-Const)`


```ascii
root@8caa5a073ec5:/# cd /tmp/saved_model
root@8caa5a073ec5:/tmp/saved_model# ls /tmp/saved_model -al --block-size=MB
total 41MB
drwxr-xr-x 4 root root  1MB Jun  6 17:05 .
drwxrwxr-x 5 1000 1000  1MB Jun  6 17:05 ..
drwxr-xr-x 2 root root  1MB Jun  2 17:58 assets
-rw-r--r-- 1 root root  4MB Jun  2 18:23 saved_model.pb
-rw-r--r-- 1 root root 20MB Jun  6 16:59 saved_model_frozen.pb
-rw-r--r-- 1 root root 17MB Jun  6 17:05 saved_model_optimized.pb
drwxr-xr-x 2 root root  1MB Jun  2 18:23 variables
root@8caa5a073ec5:/tmp/saved_model# ls variables -al --block-size=MB
total 17MB
drwxr-xr-x 2 root root  1MB Jun  2 18:23 .
drwxr-xr-x 4 root root  1MB Jun  6 17:05 ..
-rw-r--r-- 1 root root 17MB Jun  2 18:23 variables.data-00000-of-00002
-rw-r--r-- 1 root root  1MB Jun  2 18:23 variables.data-00001-of-00002
-rw-r--r-- 1 root root  1MB Jun  2 18:23 variables.index
```