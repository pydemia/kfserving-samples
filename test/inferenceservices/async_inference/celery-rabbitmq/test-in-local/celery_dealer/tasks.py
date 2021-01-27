#from __future__ import absolute_import
from .celery import app as celery_app
from .test_inference import predict
import time


@celery_app.task
def longtime_job_add(x, y):
    print('long time task begins')
    # sleep 5 seconds
    time.sleep(30)
    print('long time task finished')
    return x + y


@celery_app.task
def celery_predict(
        img_url=None,
        cluster_ip=None,
        hostname=None,
        model_name=None,
        ):
    print('long time task begins')
    res = predict(
        img_url=img_url,
        cluster_ip=cluster_ip,
        hostname=hostname,
        model_name=model_name,
    )
    print('long time task finished')
    return res


@celery_app.task
def celery_explain(
        img_url=None,
        cluster_ip=None,
        hostname=None,
        model_name=None,
        ):
    print('long time task begins')
    res = explain(
        img_url=img_url,
        cluster_ip=cluster_ip,
        hostname=hostname,
        model_name=model_name,
    )
    print('long time task finished')
    return res
