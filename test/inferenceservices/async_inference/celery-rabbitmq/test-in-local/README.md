# Test in local

## Setting

```sh
./dummy-serving/build_docker
./celery_dealer/build_docker
```

### `docker-compose`

```sh
mkdir -p $HOME/.local/bin
curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o $HOME/.local/bin/docker-compose && \
chmod +x $HOME/.local/bin/docker-compose
```

```sh
$ docker-compose -p queue-test up -d
Creating network "queue-test_default" with the default driver
Creating queue-test_rabbitmq_1      ... done
Creating queue-test_redis_1         ... done
Creating queue-test_predictor_1     ... done
Creating queue-test_celery-dealer_1 ... done

$ docker network ls
NETWORK ID          NAME                    DRIVER              SCOPE
f9da6d593fb4        bridge                  bridge              local
5016da991fcb        host                    host                local
...                 ...                     ...                 ...
79b5d5834ebc        queue-test_default      bridge              local
# docker-compose down
# docker-compose -p queue-test down 
```


```sh

MODEL_NAME="test-prd"
CLUSTER_IP="localhost:8501"
SERVICE_HOSTNAME="predictor"#"queue-test_predictor_1"
INPUT_PATH="@./input_test.json"

# curl -v -H "Host: ${SERVICE_HOSTNAME}" http://localhost:8501/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
curl -v -H "Host: mobilenet-prd" http://104.198.233.27/v1/models/mobilenet-prd:predict -d @./input_numpy.json
curl -v -H "Host: mobilenet-prd" http://mobilenet-prd/v1/models/mobilenet-prd:predict -d @./input_numpy.json

python celery_demo/test_inference.py \
    --img_url input_test.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict
```

#### Celery Dev Mode

```sh
docker run --rm -it \
    --entrypoint bash \
    --mount src="$(pwd)/celery_dealer",target=/tmp/celery_dealer,type=bind \
    --workdir /tmp/celery \
    python:3.7-slim

MODEL_NAME="test-prd"
CLUSTER_IP="localhost:8501"
SERVICE_HOSTNAME="predictor"#"queue-test_predictor_1"
INPUT_PATH="@./input_test.json"
python test_inference.py \
    --img_url input_test.json \
    --cluster_ip $CLUSTER_IP \
    --model_name $MODEL_NAME \
    --hostname $SERVICE_HOSTNAME \
    --op predict
```


```sh
# In celery container
python -m celery_dealer.run_predict
python -m celery_dealer.run_tasks
```

Redis

```sh
$ redis-cli -a kfs
Warning: Using a password with '-a' or '-u' option on the command line interface may not be safe.
127.0.0.1:6379> ping
PONG
```

```sh
127.0.0.1:6379> keys *
1) "celery-task-meta-0c54624c-4086-4650-ae50-c2a7fa04cafa"
2) "celery-task-meta-a7d74b79-7e5f-4090-8a82-197a5864bfa4"
3) "celery-task-meta-dfed676f-2078-4bca-8751-b5ac3e581af0"
4) "celery-task-meta-ad3a3003-3040-4064-8785-fa784c839302"
```

```sh
127.0.0.1:6379> get "celery-task-meta-ad3a3003-3040-4064-8785-fa784c839302"
"{\"status\": \"FAILURE\", \"result\": {\"exc_type\": \"FileNotFoundError\", \"exc_message\": [2, \"No such file or directory\"], \"exc_module\": \"builtins\"}, \"traceback\": \"Traceback (most recent call last):\\n  File \\\"/usr/local/lib/python3.7/site-packages/celery/app/trace.py\\\", line 412, in trace_task\\n    R = retval = fun(*args, **kwargs)\\n  File \\\"/usr/local/lib/python3.7/site-packages/celery/app/trace.py\\\", line 681, in __protected_call__\\n    return self.run(*args, **kwargs)\\n  File \\\"/celery_dealer/tasks.py\\\", line 28, in celery_predict\\n    model_name=model_name,\\n  File \\\"/celery_dealer/test_inference.py\\\", line 249, in predict\\n    op='predict',\\n  File \\\"/celery_dealer/test_inference.py\\\", line 121, in request\\n    with open(img_url, 'r') as f:\\nFileNotFoundError: [Errno 2] No such file or directory: 'input_test.json'\\n\", \"children\": [], \"date_done\": \"2020-06-01T17:46:54.465370\", \"task_id\": \"ad3a3003-3040-4064-8785-fa784c839302\"}"
127.0.0.1:6379> get "celery-task-meta-0c54624c-4086-4650-ae50-c2a7fa04cafa"
"{\"status\": \"SUCCESS\", \"result\": {\"predictions\": [\"111\"]}, \"traceback\": null, \"children\": [], \"date_done\": \"2020-06-01T17:49:01.021693\", \"task_id\": \"0c54624c-4086-4650-ae50-c2a7fa04cafa\"}"
```