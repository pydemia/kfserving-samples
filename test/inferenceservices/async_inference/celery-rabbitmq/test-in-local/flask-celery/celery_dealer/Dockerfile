FROM python:3.7-slim

RUN pip install \
    celery
RUN pip install -U "celery[redis]"

RUN pip install \
    matplotlib \
    tensorflow==1.15.3 \
    alibi==0.3.2

RUN mkdir -p /celery_dealer

COPY ./__init__.py /celery_dealer/__init__.py
COPY ./celery.py /celery_dealer/celery.py
COPY ./tasks.py /celery_dealer/tasks.py
COPY ./run_tasks.py /celery_dealer/run_tasks.py
COPY ./run_predict.py /celery_dealer/run_predict.py

COPY ./input_test.json /celery_dealer/input_test.json
COPY ./test_inference.py /celery_dealer/test_inference.py

RUN echo '#!/bin/bash \n\n\
  celery -A celery_dealer worker --loglevel=debug' > /usr/local/bin/init_celery.sh \
  && chmod +x /usr/local/bin/init_celery.sh

WORKDIR /

ENTRYPOINT ["init_celery.sh"]
