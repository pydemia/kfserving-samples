#FROM python:3.7-slim
FROM pydemia/mobilenet_transformer:tf1.15.2-0.1.1

RUN mkdir -p /workspace
WORKDIR /workspace

COPY mobilenet_transformer.py mobilenet_transformer.py
COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get install libgtk2.0-dev -y && \
    apt-get clean && \
    apt-get autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN pip install --upgrade pip && pip install kfserving
RUN pip install -r requirements.txt

RUN rm requirements.txt

ENTRYPOINT ["python", "-m", "mobilenet_transformer"]