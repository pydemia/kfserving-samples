
# %%
import argparse
import matplotlib.pyplot as plt
from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions
from alibi.datasets import fetch_imagenet
import numpy as np
import requests
import json
import os
from PIL import Image
import ssl
import urllib


import asyncio
import aiohttp

import tqdm

from .utils import show_img, decode_response


# @asyncio.coroutine
async def request_coroutine(
        session, img_data,
        cluster_ip=None, hostname=None, model_name=None,
        op='predict'
        ):

    data = img_data
    images = preprocess_input(data)
    requested = True

    payload = {
        "instances": [images[0].tolist()]
    }

    RESTAPI_TEMPLATE = 'http://{0}/v1/models/{1}:{2}'

    # sending post request to TensorFlow Serving server
    headers = {'Host': hostname}
    url = RESTAPI_TEMPLATE.format(cluster_ip, model_name, op)
    #print("Calling ", url)
    # response = requests.post(url, json=payload, headers=headers)
    async with session.post(url, json=payload, headers=headers) as r:
        assert r.status == 200

        return await r, op


# @asyncio.coroutine
async def explain_coroutine(
        img_data,
        cluster_ip=None, hostname=None, model_name=None,
        ):

    # resp_pred, _ = yield from request_coroutine(
    #     img_url=img_url,
    #     cluster_ip=cluster_ip,
    #     hostname=hostname,
    #     model_name=model_name,
    #     op='predict',
    # )
    # resp = json.loads(resp_pred.content.decode('utf-8'))
    # label = resp['pred_decode']
    # print(label)
    timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(timeout=timeout) as client_sess:
        response, op = await request_coroutine(
            client_sess,
            img_data=img_data,
            cluster_ip=cluster_ip,
            hostname=hostname,
            model_name=model_name,
            op='explain',
        )
        # fig = decode_response(response, op)
    return response

# %%

# @asyncio.coroutine


async def explain_coroutine_semaphore(
        img_data=None,
        cluster_ip=None, hostname=None, model_name=None,
        semaphore=None,
        ):

    # resp_pred, _ = yield from request_coroutine(
    #     img_url=img_url,
    #     cluster_ip=cluster_ip,
    #     hostname=hostname,
    #     model_name=model_name,
    #     op='predict',
    # )
    # resp = json.loads(resp_pred.content.decode('utf-8'))
    # label = resp['pred_decode']
    # print(label)
    with (await semaphore):
        async with aiohttp.ClientSession() as client_sess:
            response, op = await request_coroutine(
                client_sess,
                img_data=img_data,
                cluster_ip=cluster_ip,
                hostname=hostname,
                model_name=model_name,
                op='explain',
            )
            #fig = decode_response(response, op)
    return response


async def explain_semaphore_main(
        img_data_list=None,
        cluster_ip=None, hostname=None, model_name=None, concur_req=2,
        ):
    sem = asyncio.Semaphore(concur_req)
    to_do = [
        explain_coroutine_semaphore(
            img_data=img_data,
            cluster_ip=cluster_ip,
            hostname=hostname,
            model_name=model_name,
            semaphore=sem,
        )
        for img_data in img_data_list
    ]
    # done, pending = await asyncio.wait(to_do, loop=loop, timeout=10)
    # wait_coro = asyncio.wait(to_do, timeout=600)
    # finished, unfinished = loop.run_until_complete(wait_coro)
    to_do_iter = asyncio.as_completed(to_do)
    to_do_iter = tqdm.tqdm(to_do_iter, total=len(img_data_list))

    for future in to_do_iter:
        try:
            res = await future
        except Exception as e:
            raise e

    return res
