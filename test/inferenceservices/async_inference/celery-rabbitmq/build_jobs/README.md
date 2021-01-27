# Deploy Celery-RabbitMQ app on Kubernetes

<https://kubernetes.io/docs/tasks/job/coarse-parallel-processing-work-queue/>

## Installation

```sh
$ curl -sL https://raw.githubusercontent.com/kubernetes/kubernetes/release-1.3/examples/celery-rabbitmq/rabbitmq-service.yaml -O && \
  curl -sL https://raw.githubusercontent.com/kubernetes/kubernetes/release-1.3/examples/celery-rabbitmq/rabbitmq-controller.yaml -O && \
  kubectl apply -f rabbitmq-service.yaml && \
  kubectl apply -f rabbitmq-controller.yaml

```

```sh
# Create a temporary interactive container
kubectl run -i --tty temp --image ubuntu:18.04
```

```sh
apt-get update && \
    apt-get install -y \
    curl ca-certificates amqp-tools python dnsutils
```

```sh
root@temp:/$ nslookup rabbitmq-service

Server:         10.122.0.10
Address:        10.122.0.10#53

Name:   rabbitmq-service.default.svc.cluster.local
Address: 10.122.2.2
```

If Kube-DNS is not setup correctly, You can also find the service IP in an env var:
```sh
$ env | grep RABBIT | grep HOST

RABBITMQ_SERVICE_SERVICE_HOST=10.122.2.2
```

```sh
export BROKER_URL=amqp://guest:guest@rabbitmq-service:5672

# Now create a queue:
/usr/bin/amqp-declare-queue --url=$BROKER_URL -q foo -d


# Publish one message to it:
/usr/bin/amqp-publish --url=$BROKER_URL -r foo -p -b Hello

# And get it back.
/usr/bin/amqp-consume --url=$BROKER_URL -q foo -c 1 cat && echo

```

Filling the Queue with tasks(ex. fill the queue with 8 messages)

```sh
/usr/bin/amqp-declare-queue --url=$BROKER_URL -q job1  -d

for f in apple banana cherry date fig grape lemon melon
do
  /usr/bin/amqp-publish --url=$BROKER_URL -r job1 -p -b $f
done
```

---

## Job Example

### Create an Image for Job

`worker.py`
```py
#!/usr/bin/env python

# Just prints standard out and sleeps for 10 seconds.
import sys
import time
print("Processing " + sys.stdin.readlines()[0])
time.sleep(10)
```

```sh
chmod +x worker.py
```

```sh
docker build -t job-wq-1 .

# Docker Hub
docker tag job-wq-1 pydemia/job-wq-1
docker push pydemia/job-wq-1

# Google Container Registry
docker tag job-wq-1 gcr.io/ds-ai-platform/job-wq-1
gcloud docker -- push gcr.io/ds-ai-platform/job-wq-1
```

### Running the Job

`job.yaml`
```yaml
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: job-wq-1
spec:
  completions: 8
  parallelism: 2
  template:
    metadata:
      name: job-wq-1
    spec:
      containers:
      - name: c
        image: gcr.io/ds-ai-platform/job-wq-1
        env:
        - name: BROKER_URL
          value: amqp://guest:guest@rabbitmq-service:5672
        - name: QUEUE
          value: job1
      restartPolicy: OnFailure
EOF
```

```sh
$ kubectl delete -f ./job.yaml
job.batch/job-wq-1 created
```

```sh
$ kubectl describe jobs/job-wq-1

Name:           job-wq-1
Namespace:      default
Selector:       controller-uid=70402e8b-a2a8-4a70-b038-8e4fae2ced32
Labels:         controller-uid=70402e8b-a2a8-4a70-b038-8e4fae2ced32
                job-name=job-wq-1
Annotations:    Parallelism:  2
Completions:    8
Start Time:     Mon, 01 Jun 2020 01:15:25 +0900
Pods Statuses:  2 Running / 0 Succeeded / 0 Failed
Pod Template:
  Labels:  controller-uid=70402e8b-a2a8-4a70-b038-8e4fae2ced32
           job-name=job-wq-1
  Containers:
   c:
    Image:      gcr.io/ds-ai-platform/job-wq-1
    Port:       <none>
    Host Port:  <none>
    Environment:
      BROKER_URL:  amqp://guest:guest@rabbitmq-service:5672
      QUEUE:       job1
    Mounts:        <none>
  Volumes:         <none>
Events:
  Type    Reason            Age   From            Message
  ----    ------            ----  ----            -------
  Normal  SuccessfulCreate  19s   job-controller  Created pod: job-wq-1-5hzcl
  Normal  SuccessfulCreate  18s   job-controller  Created pod: job-wq-1-42jlm
```

After a little bit later:

```sh
$ 
```

---
## Further Reading

* [Job Patterns](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/#job-patterns)
* [Fine Parallel Processing Using a Work Queue](https://kubernetes.io/docs/tasks/job/fine-parallel-processing-work-queue/)