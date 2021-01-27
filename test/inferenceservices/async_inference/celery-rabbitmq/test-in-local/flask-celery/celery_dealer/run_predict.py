from .tasks import celery_predict
import time


"""
Methods
  delay: manage asynchronous tasks
  ready: return True if a task is done, else False

Attributes
  result: a returned object. return None if the job is not done yet.
"""


IMG_URL = 'input_test.json'
CLUSTER_IP = 'predictor:8501'
HOSTNAME = 'predictor'
MODEL_NAME = 'test-prd'


if __name__ == '__main__':
    result = celery_predict.delay(
        img_url=IMG_URL,
        cluster_ip=CLUSTER_IP,
        hostname=HOSTNAME,
        model_name=MODEL_NAME,
    )
    # at this time, our task is not finished, so it will return False
    print('Task finished? ', result.ready())
    print('Task result: ', result.result)
    # sleep 10 seconds to ensure the task has been finished
    time.sleep(5)
    # now the task should be finished and ready method will return True
    print('Task finished? ', result.ready())
    print('Task result: ', result.result)
