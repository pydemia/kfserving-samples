#!/bin/bash

# For Cleaning-up
rm -rf /tmp/__pycache__

saved_model_cli show \
    --dir /tmp/saved_model \
    --tag_set serve \
    --signature_def serving_default