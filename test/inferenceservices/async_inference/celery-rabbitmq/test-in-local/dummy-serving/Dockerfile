FROM python:3.6-slim

ENV MODEL_BASE_PATH=/models
RUN mkdir -p ${MODEL_BASE_PATH}
ENV MODEL_NAME=model

ARG CUDA_VISIBLE_DEVICES
ENV CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES

WORKDIR /tmp

RUN pip install \
    contextlib2 opencv-python Flask flask-restful jsonify

COPY runserver.py /tmp


# RUN chmod u+x /usr/local/bin/init_entrypoint.sh
EXPOSE 8500 8501

# https://github.com/tensorflow/serving/blob/master/tensorflow_serving/tools/docker/Dockerfile
# Create a script that runs the model server so we can use environment variables
# while also passing in arguments from the docker command line
RUN echo '#!/bin/bash \n\n\
    python runserver.py --port=8500 --rest_api_port=8501 \
    --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} \
    "$@"' > /usr/local/bin/init_entrypoint.sh \
    && chmod +x /usr/local/bin/init_entrypoint.sh

ENTRYPOINT ["init_entrypoint.sh"]