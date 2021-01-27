# Templates for `inferenceservice`

##

```sh
git clone \
    --single-branch \
    -b v0.3.0 \
    https://github.com/kubeflow/kfserving kfserving-python && \
cd kfserving-python && \
git filter-branch --subdirectory-filter python HEAD && \
cd ..
```