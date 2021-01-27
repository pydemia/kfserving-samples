from __future__ import absolute_import
import os
from celery import Celery


PKG_NAME = 'celery_dealer'

# BROKER_URL_OUTER = 'amqp://kfs:kfs@kfs.pydemia.org:5672'
# BROKER_URL_INNER = 'amqp://kfs:kfs@rabbitmq.ifsvc-queue.svc.clusters.local:5672'

# REDIS_BROKER = 'redis://:kfs@redis-master.ifsvc-queue.svc.clusters.local:6379/0'
# REDIS_BACKEND = 'redis://:kfs@redis-master.ifsvc-queue.svc.clusters.local:6379/1'

# REDIS_BROKER_LOCAL = 'redis://:kfs@redis-master:6370/0'
# REDIS_BACKEND_LOCAL = 'redis://:kfs@redis-master:6370/1'

BROKER_URL = 'amqp://kfs:kfs@rabbitmq:5672'
# REDIS_BROKER = 'redis://:kfs@redis-master:6370/0'
REDIS_BACKEND = 'redis://:kfs@redis:6379/0'

app = Celery(
    PKG_NAME,
    # backend='rpc://',
    backend=REDIS_BACKEND,
    broker=BROKER_URL,
    include=[f'{PKG_NAME}.tasks'],
)
