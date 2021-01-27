# %%
import matplotlib.pyplot as plt

import asyncio
import aiohttp
import tqdm

import nest_asyncio
# nest_asyncio.apply()

import importlib
import src

importlib.reload(src)

# %%
OP = 'explain'
IMG_URL = None
CLUSTER_IP = '104.198.233.27'
HOSTNAME = 'mobilenet-fullstack.ifsvc.104.198.233.27.xip.io'
MODEL_NAME = 'mobilenet-fullstack'

op = OP
img_url = IMG_URL
img_url_list = [IMG_URL]
cluster_ip = CLUSTER_IP
hostname = HOSTNAME
model_name = MODEL_NAME

server_kwargs = dict(
    cluster_ip=CLUSTER_IP,
    hostname=HOSTNAME,
    model_name=MODEL_NAME,
)

# %%
src.utils.get_image_data
request = src.request.request_coroutine
explain = src.request.explain_coroutine

img_data = src.utils.get_image_data()
img_url = 'https://raw.githubusercontent.com/pydemia/containers/master/kubernetes/apps/kfserving/examples/mobilenet/squirrel.jpg'
img_data_list = [
    img_data,
    src.utils.get_image_data(img_url=img_url)
]

fig, axes = plt.subplots(1, 2)
for ax, img in zip(axes.ravel(), img_data_list):
    ax.imshow(img[0])
# %%

request
explain


# %% ========================================
# loop = asyncio.get_event_loop()
# to_do = [
#     explain(
#         img_data=img_data,
#         cluster_ip=cluster_ip,
#         hostname=hostname,
#         model_name=model_name,
#     )
#     for img_data in img_data_list
# ]
# #done, pending = await asyncio.wait(to_do, loop=loop, timeout=10)
# #wait_coro = asyncio.wait(to_do, loop=loop, timeout=600)
# wait_coro = asyncio.wait(to_do, timeout=600)
# # loop.stop()
# # loop.close()
# finished, unfinished = loop.run_until_complete(wait_coro)
# loop.close()

# %% ========================================

explain_coroutine_semaphore = src.request.explain_coroutine_semaphore


async def explain_semaphore_multi(
        img_data_list=None,
        cluster_ip=None, hostname=None, model_name=None, concur_req=3,
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


# %% ========================================

loop = asyncio.get_event_loop()
coro = explain_semaphore_multi(
    img_data_list=img_data_list,
    concur_req=2,
    **server_kwargs,
)
res = loop.run_until_complete(coro)
loop.close()


res

# %% ========================================

loop = asyncio.get_event_loop()
loop.run_in_executor(
    None,
    explain_coroutine_semaphore,
)
coro = explain_semaphore_multi(
    img_data_list=img_data_list,
    concur_req=2,
    **server_kwargs,
)
res = loop.run_until_complete(coro)
loop.close()
