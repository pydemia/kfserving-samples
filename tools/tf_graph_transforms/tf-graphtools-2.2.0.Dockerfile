FROM tensorflow/tensorflow:2.2.0

RUN apt-get update && \
  apt-get install -y \
  build-essential \
  vim htop sudo \
  libcurl4-openssl-dev \
  libssl-dev wget curl unzip \
  git cmake tree

# # Set Locale
# RUN apt-get update -y && \
#     apt-get install -y locales && \
#     locale-gen --purge "en_US.UTF-8"


# RUN echo 'LC_ALL=en_US.UTF-8' >> /etc/environment
# RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen
# RUN echo 'LANG=en_US.UTF-8' > /etc/locale.conf


# # Install Conda

# RUN apt-get update --fix-missing && \
#     apt-get install -y \
#     wget bzip2 ca-certificates \
#     libglib2.0-0 libxext6 libsm6 libxrender1 \
#     git mercurial subversion acl

# RUN apt-get install -y \
#     libgl1-mesa-glx libegl1-mesa \
#     libxrandr2 libxrandr2 libxss1 \
#     libxcursor1 libxcomposite1 libasound2 \
#     libxi6 libxtst6


# GCLOUD
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && \
    apt-get update -y && \
    apt-get install google-cloud-sdk -y

# AWS CLI 1 (for `/usr/bin/python`)
# RUN apt update && apt add \
#         ca-certificates \
#         groff \
#         less \
#         python \
#         py-pip && \
#     rm -rf /var/cache/apt/* && \
#     pip3 install pip --upgrade && \
#     pip3 install awscli

# AWS CLI 2
RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf /aws && \
    rm awscliv2.zip

# AZURE CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# For onnx(INSTALL IN NON-CONDA ENVIRONMENT)
RUN apt install cmake protobuf-compiler libprotoc-dev -y


# # -------------------------------------------------------------------- #
# # Install "software-properties-common" (for the "add-apt-repository")
# RUN apt-get update && \
#   apt-get install -y \
#   software-properties-common

# # Install default-jdk
# RUN apt-get update && \
#   apt-get install -y default-jdk && \
#   apt-get clean


# # Setup JAVA_HOME -- useful for docker commandline
# ENV JAVA_HOME /usr/lib/jvm/default-java
# RUN echo 'export JAVA_HOME="/usr/lib/jvm/default-java"' >> /etc/profile


# Install node.js & npm
RUN apt-get update && \
    # apt-get -y install curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_12.x  | bash - && \
    apt-get -y install nodejs && \
    npm install -g npm

RUN npm install -g @bazel/bazelisk


ENV TFVERSION=2.2.0

#### THIS IMAGE ALREADY HAS `saved_model_cli` in this path.
RUN git clone --single-branch -b "v$TFVERSION" https://github.com/tensorflow/tensorflow /tensorflow && \
    cd /tensorflow && \
    bazel build tensorflow/tools/graph_transforms:summarize_graph && \
    bazel build tensorflow/tools/graph_transforms:transform_graph && \
    # bazel build tensorflow/python/tools:saved_model_cli && \
    bazel build tensorflow/python/tools:freeze_graph && \
    bazel build tensorflow/python/tools:optimize_for_inference && \
    cd /
RUN cd /tensorflow && \
    bazel build -c opt tensorflow/tools/benchmark:benchmark_model && \
    cd /

#--action_env PYTHON_BIN_PATH=/usr/bin/python3
#--host_javabase=@local_jdk//:jdk
RUN ln -s "/tensorflow/bazel-bin/tensorflow/tools/graph_transforms/summarize_graph" \
    /usr/local/bin/summarize_graph
RUN ln -s "/tensorflow/bazel-bin/tensorflow/tools/graph_transforms/transform_graph" \
    /usr/local/bin/transform_graph
# RUN ln -s "/tensorflow/bazel-bin/tensorflow/python/tools/saved_model_cli" \
#     /usr/local/bin/saved_model_cli
RUN ln -s "/tensorflow/bazel-bin/tensorflow/python/tools/freeze_graph" \
    /usr/local/bin/freeze_graph
RUN ln -s "/tensorflow/bazel-bin/tensorflow/python/tools/optimize_for_inference" \
    /usr/local/bin/optimize_for_inference
RUN ln -s "/tensorflow/bazel-bin/tensorflow/tools/benchmark/benchmark_model" \
    /usr/local/bin/benchmark_model
RUN echo '#!/bin/bash\n\npython /tensorflow/tensorflow/python/tools/inspect_checkpoint.py' > /usr/local/bin/inspect_checkpoint && \
    chmod +x /usr/local/bin/inspect_checkpoint

# RUN git clone -b v2.2.0 https://github.com/tensorflow/tensorflow $WORKDIR/tensorflow-2.2.0 && \
#     cd $WORKDIR/tensorflow-2.2.0 && \
#     bazel build tensorflow/tools/graph_transforms:summarize_graph && \
#     bazel build tensorflow/tools/graph_transforms:transform_graph && \
#     bazel build tensorflow/python/tools:freeze_graph && \
#     bazel build tensorflow/python/tools:optimize_for_inference && \
#     cd /
#     #--action_env PYTHON_BIN_PATH=/usr/bin/python3
#     #--host_javabase=@local_jdk//:jdk
# RUN ln -s "$WORKDIR/tensorflow-2.2.0/bazel-bin/tensorflow/tools/graph_transforms/summarize_graph" \
#     /usr/local/bin/summarize_graph2
# RUN ln -s "$WORKDIR/tensorflow-2.2.0/bazel-bin/tensorflow/tools/graph_transforms/transform_graph" \
#     /usr/local/bin/transform_graph2
# RUN ln -s "$WORKDIR/tensorflow-2.2.0/bazel-bin/tensorflow/python/tools/saved_model_cli" \
#     /usr/local/bin/saved_model_cli2
# RUN ln -s "$WORKDIR/tensorflow-2.2.0/bazel-bin/tensorflow/python/tools/freeze_graph" \
#     /usr/local/bin/freeze_graph2
# RUN ln -s "$WORKDIR/tensorflow-2.2.0/bazel-bin/tensorflow/python/tools/optimize_for_inference" \
#     /usr/local/bin/optimize_for_inference2

# ENV TFVERSION=2

# RUN echo '#!/bin/bash \n\n\
# if [ $TFVERSION == 1 ]; then \n\
#   ln -s /usr/local/bin/summarize_graph1 /usr/local/bin/summarize_graph \n\
#   ln -s /usr/local/bin/transform_graph1 /usr/local/bin/transform_graph \n\
#   ln -s /usr/local/bin/saved_model_cli1 /usr/local/bin/saved_model_cli \n\
#   ln -s /usr/local/bin/freeze_graph1 /usr/local/bin/freeze_graph \n\
#   ln -s /usr/local/bin/optimize_for_inference1 /usr/local/bin/optimize_for_inference \n\
# else \
#   ln -s /usr/local/bin/summarize_graph2 /usr/local/bin/summarize_graph \n\
#   ln -s /usr/local/bin/transform_graph2 /usr/local/bin/transform_graph \n\
#   ln -s /usr/local/bin/saved_model_cli2 /usr/local/bin/saved_model_cli \n\
#   ln -s /usr/local/bin/freeze_graph2 /usr/local/bin/freeze_graph \n\
#   ln -s /usr/local/bin/optimize_for_inference2 /usr/local/bin/optimize_for_inference \n\
# fi \n\
# ' > /usr/local/bin/init_entrypoint.sh \
#   && chmod +x /usr/local/bin/init_entrypoint.sh

ENTRYPOINT ["/bin/bash"]
