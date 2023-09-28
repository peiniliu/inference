"""
pytorch local backend 
"""
# pylint: disable=unused-argument,missing-docstring
#import torch
#import torchvision
from argparse import ArgumentParser

import mmcv

from mmcls.apis import inference_model, init_model, show_result_pyplot


import backend
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("pytorch-local")


class BackendPytorchLocal(backend.Backend):
    def __init__(self):
        super(BackendPytorchLocal, self).__init__()
        self.config = None
        self.model = None
        self.device = "cpu"
        #self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

    def version(self):
        return mmcv.__version__

    def name(self):
        return "pytorch-local"

    def image_format(self):
        return "NCHW"

    def load(self, model_path, inputs=None, outputs=None):
        #here the inputs is config
        self.config = inputs[0]
        # build the model from a config file and a checkpoint file
        self.model = init_model(self.config, model_path, device=self.device)
        log.info("config {}; model {}".format(self.config, self.model))

        return self

    def predict(self, data):
        # test a image
        # log.error("PEINI: number of response label {}".format(data[0]))
        result = inference_model(self.model, data[0])
        # log.error("PEINI: number of response label {}".format(result))
        return [result]
