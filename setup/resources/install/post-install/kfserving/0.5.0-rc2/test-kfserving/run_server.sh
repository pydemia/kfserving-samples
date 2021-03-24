#!/bin/bash

set -e

export MODEL_ANO=VAE_GAN_HYUP_255_V2
export MODEL_CLS_SEQ=densenet121_mixed_precision
export GPU_ID=AUTO

python3 hm_server.py