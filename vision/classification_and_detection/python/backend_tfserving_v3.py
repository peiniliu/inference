"""
tf-serving V2
"""

from __future__ import print_function
from tkinter import Image
# pylint: disable=unused-argument,missing-docstring,useless-super-delegation

import tensorflow as tf
from tensorflow.core.framework import graph_pb2

import backend


# This is a placeholder for a Google-internal import.

import grpc
import requests
import json 

#from tensorflow_serving.apis import predict_pb2
#from tensorflow_serving.apis import prediction_service_pb2_grpc

import base64
import numpy as np 
import cv2
from PIL import Image
import io

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BackendTfservingV3")


class BackendTfservingV3(backend.Backend):
    def __init__(self):
        super(BackendTfservingV3, self).__init__()

    def version(self):
        return tf.__version__ + "/" + tf.__git_version__

    def name(self):
        return "tfserving_v3"

    def image_format(self):
        # By default tensorflow uses NHWC (and the cpu implementation only does NHWC)
        return "NHWC"

    def load(self, inputs=None, outputs=None, server=None):
        # there is no input/output meta data i the graph so it need to come from config.
        log.info("PEINI: server address {}".format(server))
#        if not inputs:
#            raise ValueError("BackendTfserving needs inputs")
#        if not outputs:
#            raise ValueError("BackendTfserving needs outputs")
        if not server:
            raise ValueError("BackendTfserving needs tfserving running model")
        self.server = server
        self.outputs = outputs
        self.inputs = inputs

        IMAGE_URL = 'https://tensorflow.org/images/blogs/serving/cat.jpg'
        # Download the image since we weren't given one
        dl_request = requests.get(IMAGE_URL, stream=True)
        dl_request.raise_for_status()
        
        jpeg_rgb = Image.open(io.BytesIO(dl_request.content))
        # jpeg_rgb = np.expand_dims(np.array(jpeg_rgb) / 255.0, 0).tolist()
        # print((np.array(jpeg_rgb) / 255.0).ndim)
        # # print(np.array(jpeg_rgb))
        # print(type((np.array(jpeg_rgb) / 255.0).tolist()))
        test=[]
        test.append((np.array(jpeg_rgb) / 255.0).tolist())
        test.append((np.array(jpeg_rgb) / 255.0).tolist())
        # print(type(np.array(jpeg_rgb)))
        # print(type((np.array(jpeg_rgb) / 255.0).tolist()))
        # print(type(test))
        predict_request = json.dumps({'instances': test})
        # print(predict_request)
        
        # img = np.load("/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/preprocessed/imagenet/NHWC/val/ILSVRC2012_val_00050000.JPEG.npy")
        # predict_request = '{"instances" : [%s]}' % img
        # print(predict_request)
        
        #restful - service port 8501- change yaml
        self.SERVER_URL = "http://"+server+"/v1/models/resnet:predict"
        log.info("PEINI url {}".format(self.SERVER_URL))
        
        response = requests.post(self.SERVER_URL, data=predict_request)
        log.info(len(response.json()['predictions']))
        if np.argmax(response.json()['predictions'][0]) != 285:
            raise ValueError("BackendTfserving backend error")
        log.info("PEINI: server is running")
        return self

    def predict(self, data):
        response = requests.post(self.SERVER_URL, data=data)
        # print(response)
        # print(np.argmax(response.json()['predictions']))
        return response
        