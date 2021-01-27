from .tasks import longtime_job_add
import time


"""
Methods
  delay: manage asynchronous tasks
  ready: return True if a task is done, else False

Attributes
  result: a returned object. return None if the job is not done yet.
"""

if __name__ == '__main__':
    result = longtime_job_add.delay(151, 149)
    # at this time, our task is not finished, so it will return False
    print('Task finished? ', result.ready())
    print('Task result: ', result.result)
    # sleep 10 seconds to ensure the task has been finished
    time.sleep(5)
    # now the task should be finished and ready method will return True
    print('Task finished? ', result.ready())
    print('Task result: ', result.result)
