"""
tensorflow backend (https://github.com/tensorflow/tensorflow)
"""

# pylint: disable=unused-argument,missing-docstring,useless-super-delegation

import tensorflow as tf
from tensorflow.core.framework import graph_pb2
from tensorflow.keras.applications.resnet50 import preprocess_input

import backend

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("Backendtflocal")


class Backendtflocal(backend.Backend):
    def __init__(self):
        super(Backendtflocal, self).__init__()

    def version(self):
        return tf.__version__ + "/" + tf.__git_version__

    def name(self):
        return "tflocal"

    def image_format(self):
        # By default tensorflow uses NHWC (and the cpu implementation only does NHWC)
        return "NHWC"

    def load(self, model_dir, inputs=None, outputs=None, preprocess=0):
        # there is no input/output meta data i the graph so it need to come from config.
        log.info("PEINI: model_dir {}".format(model_dir))
        #if not inputs:
        #    raise ValueError("BackendTensorflow needs inputs")
        #if not outputs:
        #    raise ValueError("BackendTensorflow needs outputs")
        self.outputs = outputs
        self.inputs = inputs
        self.preprocess = preprocess

        self.model = tf.saved_model.load(model_dir, tags=None, options=None)
        log.info("PEINI: signature list {}".format(list(self.model.signatures.keys())))
        signatures = list(self.model.signatures.keys())
        self.infer = self.model.signatures[signatures[0]]
        return self

    def predict(self, img):
        print(img.shape)
        if self.preprocess == 0:
            img = preprocess_input(img)
        preds = self.infer(tf.constant(img))[self.outputs[0]]

        return preds

 
