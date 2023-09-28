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
log = logging.getLogger("pytorch-server")

import requests
import json

class BackendPytorchServer(backend.Backend):
    def __init__(self):
        super(BackendPytorchServer, self).__init__()
        self.servers = []
        self.device = "cpu"
        self.current_server = 0
        #self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

    def version(self):
        return mmcv.__version__

    def name(self):
        return "pytorch-server"

    def image_format(self):
        return "NCHW"

    def load(self, model_path, inputs=None, outputs=None):
        #here the inputs is server
        for server in inputs:
            self.servers.append("http://"+server+"/predictions/"+model_path)
        log.info("servers {}".format(self.servers))
        print(self.servers)

        return self

    def predict(self, data):
        # test a image
        # log.error("PEINI: number of response label {}".format(data))
        # response = requests.post(self.servers[self.current_server], files={'data': open(data[0], 'rb')})
        # Inference single image by torchserve engine.
        # with open(args.img, 'rb') as image:
        #     response = requests.post(url, image)
        # server_result = response.json()
        # show_result_pyplot(model, args.img, server_result, title='server_result')
        
        with open(data[0], 'rb') as image:
            response = requests.post(self.servers[self.current_server], image)
        # print(json.loads(response.content))
        self.current_server = (self.current_server + 1) % len(self.servers)
        print(self.servers[self.current_server], response.json())
        
        # print(json.loads(response.content)['pred_label'])
        return [json.loads(response.content)]
