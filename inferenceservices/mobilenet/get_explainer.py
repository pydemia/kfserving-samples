
from tensorflow.keras.applications.mobilenet import MobileNet
from alibi.datasets import fetch_imagenet
from alibi.explainers import AnchorImage
import dill

model = MobileNet(weights='imagenet')


# def predict_fn(x): return model.predict(x)
predict_fn = lambda x: x


segmentation_fn = 'slic'
kwargs = {'n_segments': 15, 'compactness': 20, 'sigma': .5}
image_shape = (224, 224, 3)
explainer = AnchorImage(
    predict_fn,
    image_shape,
    segmentation_fn=segmentation_fn,
    segmentation_kwargs=kwargs,
    images_background=None,
)


# Clear explainer predict_fn as its a lambda and will be reset when loaded
explainer.predict_fn = None
with open("explainer.dill", 'wb') as f:
    dill.dump(explainer, f)
