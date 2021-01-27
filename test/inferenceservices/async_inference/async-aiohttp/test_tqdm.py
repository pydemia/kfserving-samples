from tqdm import tqdm, trange
from time import sleep


# Iterable-based
# %%
text = ""
for char in tqdm(["a", "b", "c", "d"]):
    sleep(0.25)
    text = text + char

# %%
for i in trange(100):
    sleep(0.01)

# %%
pbar = tqdm(["a", "b", "c", "d"])
for char in pbar:
    sleep(0.25)
    pbar.set_description("Processing %s" % char)

# %%
with tqdm(total=100) as pbar:
    for i in range(10):
        sleep(0.1)
        pbar.update(10)


# %%
