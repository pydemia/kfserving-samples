# Celery and RabbitMQ

## Install `RabbitMQ` on a Kubernetes Cluster

RERUIRE: `helm`([Set up](https://github.com/pydemia/containers/blob/master/kubernetes/apps/helm/README.md#create-tiller-service-account-and-assign-cluster-admin-role-then-initiate-helm--install-tiller))

* Namespace: `ifsvc`

[Ref](https://hub.helm.sh/charts/bitnami/rabbitmq)

```sh
NAMESPACE_QUEUE="ifsvc-queue"
kubectl create ns $NAMESPACE_QUEUE
kubectl label ns $NAMESPACE_QUEUE istio-injection=enabled
helm repo add bitnami https://charts.bitnami.com/bitnami

# helm install --name kfs-rabbitmq bitnami/rabbitmq --namespace rabbitmq
# helm del --purge kfs-rabbitmq
helm install --name rabbitmq \
  --set rabbitmq.username=kfs,rabbitmq.password=kfs,rabbitmq.erlangCookie=secretcookie \
    bitnami/rabbitmq \
    --namespace $NAMESPACE_QUEUE

```


### Expose RabbitMQ
```sh
$ NAMESPACE_QUEUE="ifsvc-queue"
$ kubectl apply -f expose-rabbitmq-ifsvc-queue.yaml

virtualservice.networking.istio.io/rabbitmq-vs created
gateway.networking.istio.io/rabbitmq-amqp-gateway created
virtualservice.networking.istio.io/rabbitmq-amqp-vs created

$ kubectl -n istio-system patch svc istio-ingressgateway \
    --type='json' \
    -p='[{"op": "add", "path": "/spec/ports/-", "value": {"name": "rabbitmq-amqp","port":5672,"protocol":"TCP","targetPort":5672}}]'

```

```

* DASHBOARD: `http://kfs.pydemia.org/ifq/rabbitmq/dashboard/`
* AMQP PORT `amqp://kfs.pydemia.org/rabbitmq/amqp/`

```sh
$ kubectl -n $NAMESPACE_QUEUE get svc

NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                                 AGE
rabbitmq            ClusterIP   10.122.14.175   <none>        4369/TCP,5672/TCP,25672/TCP,15672/TCP   17m
rabbitmq-headless   ClusterIP   None            <none>        4369/TCP,5672/TCP,25672/TCP,15672/TCP   17m
```

### (Optional) Start RabbitMQ with Docker

```sh
docker run --hostname rmq \
    -p 5672:5672 \
    -p 8080:15672 \
    -e RABBITMQ_DEFAULT_USER=guest \
    -e RABBITMQ_DEFAULT_PASS=guest \
    --name rabbitmq \
    rabbitmq:3-management
```

---

## Install `redis` to store results

<https://bitnami.com/stack/redis/helm>
<https://github.com/bitnami/charts/tree/master/bitnami/redis/#installing-the-chart>
<https://docs.celeryproject.org/en/latest/userguide/tasks.html#task-result-backends>
<https://docs.celeryproject.org/en/latest/userguide/configuration.html#conf-result-backend>

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install --name redis \
  --set password=kfs \
    bitnami/redis \
    --namespace $NAMESPACE_QUEUE
```

Then, the output would be:
```ascii
NAME:   redis
LAST DEPLOYED: Mon Jun  1 21:49:28 2020
NAMESPACE: ifsvc-queue
STATUS: DEPLOYED

RESOURCES:
==> v1/ConfigMap
NAME          DATA  AGE
redis         3     2s
redis-health  6     2s

==> v1/Pod(related)
NAME            READY  STATUS   RESTARTS  AGE
redis-master-0  0/2    Pending  0         0s
redis-slave-0   0/2    Pending  0         1s

==> v1/Secret
NAME   TYPE    DATA  AGE
redis  Opaque  1     2s

==> v1/Service
NAME            TYPE       CLUSTER-IP    EXTERNAL-IP  PORT(S)   AGE
redis-headless  ClusterIP  None          <none>       6379/TCP  2s
redis-master    ClusterIP  10.122.7.235  <none>       6379/TCP  2s
redis-slave     ClusterIP  10.122.6.135  <none>       6379/TCP  2s

==> v1/StatefulSet
NAME          READY  AGE
redis-master  0/1    2s
redis-slave   0/2    2s


NOTES:
** Please be patient while the chart is being deployed **
Redis can be accessed via port 6379 on the following DNS names from within your cluster:

redis-master.ifsvc-queue.svc.cluster.local for read/write operations
redis-slave.ifsvc-queue.svc.cluster.local for read-only operations


To get your password run:

    export REDIS_PASSWORD=$(kubectl get secret --namespace ifsvc-queue redis -o jsonpath="{.data.redis-password}" | base64 --decode)

To connect to your Redis server:

1. Run a Redis pod that you can use as a client:

   kubectl run --namespace ifsvc-queue redis-client --rm --tty -i --restart='Never' \
    --env REDIS_PASSWORD=$REDIS_PASSWORD \
   --image docker.io/bitnami/redis:6.0.4-debian-10-r0 -- bash

2. Connect using the Redis CLI:
   redis-cli -h redis-master -a $REDIS_PASSWORD
   redis-cli -h redis-slave -a $REDIS_PASSWORD

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace ifsvc-queue svc/redis-master 6379:6379 &
    redis-cli -h 127.0.0.1 -p 6379 -a $REDIS_PASSWORD

```

Test `redis`:

```sh
$ kubectl port-forward --namespace ifsvc-queue svc/redis-master 6379:6379 &
    redis-cli -h 127.0.0.1 -p 6379 -a $REDIS_PASSWORD

[1] 25571
Forwarding from [::1]:6379 -> 6379

127.0.0.1:6379> 
127.0.0.1:6379> set testkey tmpvalue
OK
127.0.0.1:6379> get testkey
"tmpvalue"
127.0.0.1:6379> exit

$ kill 25571

[1]  + 25571 terminated  kubectl port-forward --namespace ifsvc-queue svc/redis-master 6379:6379
```

Test `redis` locally:
```sh
docker run --rm -it \
    --name redis-master \
    -e REDIS_PASSWORD=passwd \
    -p 6370:6379/tcp \
    bitnami/redis:latest
```

---
## Install `celery`

```sh
# conda activate kfserving
pip install celery
```
### Build an celery app

```sh
celery_demo
├── celery.py  # It's name should be `celery.py`
├── run_tasks.py
└── tasks.py
```

If `celery.py` not exist, you will meet this message:

```ascii
Error: 
Unable to load celery application.
Module 'celery_demo' has no attribute 'celery'
```


### Run the celery worker server
```sh
$ celery -A celery_demo worker --loglevel=info

 -------------- celery@pydemia-server v4.4.2 (cliffs)
--- ***** ----- 
-- ******* ---- Linux-4.4.0-179-generic-x86_64-with-debian-stretch-sid 2020-05-31 23:22:57
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         celery_demo:0x7f49c185d5d0
- ** ---------- .> transport:   amqp://kfs:**@kfs.pydemia.org:5672//
- ** ---------- .> results:     rpc://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . celery_demo.tasks.add_longtime_job

[2020-05-31 23:22:57,927: INFO/MainProcess] Connected to amqp://kfs:**@kfs.pydemia.org:5672//
[2020-05-31 23:22:58,902: INFO/MainProcess] mingle: searching for neighbors
[2020-05-31 23:23:02,249: INFO/MainProcess] mingle: all alone
[2020-05-31 23:23:04,547: INFO/MainProcess] celery@pydemia-server ready.
```

Run this at the same time:
```sh
python -m celery_demo.run_tasks
```

---

# Test in `local`

* `rabbitmq`
```sh
docker run --rm -it \
    --name rabbitmq \
    -p 15672:15672/tcp \
    -p 25672:25672/tcp \
    -p 4369:4369/tcp \
    -p 5672:5672/tcp \
    bitnami/rabbitmq:latest

```

* `redis`
```sh
docker run --rm -it \
    --name redis-master \
    -e REDIS_PASSWORD=passwd \
    -p 6370:6379/tcp \
    bitnami/redis:latest
```