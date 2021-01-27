FROM tensorflow/tensorflow:1.15.2-gpu-py3-jupyter

RUN apt-get install -y \
    libsm6 libxext6 libxrender-dev

RUN pip install \
    opencv-python \
    GPUtil \
    Pillow


# CHANGED: ai_modeling_hemorrhage.py:26:
# GPU_ID = str(GPUtil.getAvailable()[0])
# GPU_ID = "-1"

COPY ./seg_test /tf/seg_test
COPY ./get_savedmodel.py /tf/seg_test/get_savedmodel.py
COPY ./clean_cache_and_show_savedmodel.sh /tf/seg_test/clean_cache_and_show_savedmodel.sh
RUN chmod +x /tf/seg_test/clean_cache_and_show_savedmodel.sh

ENTRYPOINT ["/bin/bash"]

