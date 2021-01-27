#! /bin/bash

# package update
yum -y update

# Install Kubectl
curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" \
&& chmod +x ./kubectl \
&& mv ./kubectl /usr/local/bin/kubectl

# Install Istioctl
curl -sL https://istio.io/downloadIstioctl | sh - \
&& mv $HOME/.istioctl/bin/istioctl /usr/local/bin/istioctl \
&& rm -rf $HOME/.istioctl

# Install JDK (Zulu14)
rpm --import http://repos.azulsystems.com/RPM-GPG-KEY-azulsystems \
&& curl -o /etc/yum.repos.d/zulu.repo http://repos.azulsystems.com/rhel/zulu.repo \
&& yum -y install zulu-14

# Install Miniconda
CONDA_USER="root"
CONDA_GRP="conda"
CONDA_DIR="/opt/miniconda3"
if [ $(getent group $CONDA_GRP) ]; then
  echo "group '$CONDA_GRP' exists."
else
  echo "creating group '$CONDA_GRP'..."
  usermod -a -G $CONDA_GRP $CONDA_USER
fi
curl -o Miniconda3-Linux-x86_64.sh https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh \
&& bash Miniconda3-Linux-x86_64.sh -b -p $CONDA_DIR -u \
&& chgrp -R $CONDA_GRP $CONDA_DIR \
&& chmod 770 -R $CONDA_DIR
# && rm Miniconda3-Linux-x86_64.sh

miniconda_bashrc="
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/pydemia/apps/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/pydemia/apps/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/pydemia/apps/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/pydemia/apps/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

#alias nblogs=cat ~/.jupyter/logs/notebook.log > ~/.jupyter/logs/notebook.log.tmp | cat

export PATH="$CONDA_DIR/bin:$PATH"
export CONDA_EXEC_PATH="$CONDA_DIR/bin/conda"
"

echo "$miniconda_bashrc" >> /etc/profile
