from __future__ import absolute_import
from celery_demo.celery import app
import time


@app.task
def longtime_job_add(x, y):
    print('long time task begins')
    # sleep 5 seconds
    time.sleep(30)
    print('long time task finished')
    return x + y
