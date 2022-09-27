"""
tf-serving
"""

from __future__ import print_function
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

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BackendTfserving")


class BackendTfserving(backend.Backend):
    def __init__(self):
        super(BackendTfserving, self).__init__()

    def version(self):
        return tf.__version__ + "/" + tf.__git_version__

    def name(self):
        return "tfserving"

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
        data = dl_request.content
        #with open("/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/test_imagenet/val/512px-Cacatua_moluccensis_-Cincinnati_Zoo-8a.jpg", 'rb') as f:
        #   data = f.read()

#        #grpc - service port 8500- change yaml
#        self.channel = grpc.insecure_channel(self.server)
#        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)
#        log.info("PEINI: finding server")
#
#        #log.info("PEINI: data={}".format(data))
#        result = self.predict(data)
#        if result[0] != 286:
#            raise ValueError("BackendTfserving backend error")
#        log.info("PEINI: server is running")

        #restful - service port 8501- change yaml
        self.SERVER_URL = "http://"+server+"/v1/models/resnet:predict"
        #self.SERVER_URL = "http://"+server+"/seldon/scanflow-ai-pa/tfserving-mobilnet/v1/models/resnet:predict"
        log.info("PEINI url {}".format(self.SERVER_URL))
        jpeg_bytes = base64.b64encode(data).decode('utf-8')
        #images = '[{"b64": "%s"}]' % jpeg_bytes
        images = '[{"b64": "%s"},{"b64": "%s"}]' % (jpeg_bytes,jpeg_bytes)
        predict_request = '{"instances" : %s}' % images
        response = requests.post(self.SERVER_URL, data=predict_request)
        #predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes
        #predict_request = '{"instances" : [{"b64": "%s"},{"b64": "%s"}]}' % (jpeg_bytes,jpeg_bytes)
        #log.info("request {}".format(predict_request))
        #log.info("PEINI: response classes {}".format(response.json()))
        results = np.array([], dtype='int16')
        for i in response.json()['predictions']:
            #log.info("len {}".format(len(response.json()['predictions'])))
            #log.info("result {}".format(i['classes']))
            results = np.append(results, i['classes'])
            #print(results) 
        result = response.json()['predictions'][0]['classes']
        if result != 286:
            raise ValueError("BackendTfserving backend error")
        log.info("PEINI: server is running")
        return self

    def predict(self, data):
#        # 1. Send request using grpc
#        # See prediction_service.proto for gRPC request/response details.
#        request = predict_pb2.PredictRequest()
#        request.model_spec.name = 'resnet'
#        request.model_spec.signature_name = 'serving_default'
#        request.inputs['image_bytes'].CopyFrom(
#            tf.make_tensor_proto(data, shape=[1]))
#        result = self.stub.Predict(request, 10.0)  # 10 secs timeout
#        print(result.outputs['classes'].int64_val[0])
#        #raise ValueError("stop")
#        #return self.sess.run(self.outputs, feed_dict=feed)
#        return result.outputs['classes'].int64_val

        # 2. Send request using restful
        predict_request = '{"instances" : %s}' % data
        #log.info("request {}".format(predict_request))
        response = requests.post(self.SERVER_URL, data=predict_request)
        #log.info("PEINI: response classes {}".format(response.json()))
        #log.info("PEINI: response classes {}".format(response.json()['predictions'][0]['classes']))
        response.raise_for_status()
        return response.json()['predictions']

       # 3. send request using restful but based on narray
       # image = "/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/test_imagenet/val/512px-Cacatua_moluccensis_-Cincinnati_Zoo-8a.jpg"
       # headers = {"content-type": "application/json"}
       # image_content = cv2.imread(image,1).astype('uint8').tolist()
       # body = {"instances": [image_content]}
       # r = requests.post(self.SERVER_URL, data=json.dumps(body), headers = headers) 
       # print(r.text)
        

#        print("request:")
#        print(feed)
#      request:
#{'input_tensor:0': array([[[[ 13.32      ,  20.220001  ,  37.059998  ],
#         [-16.68      ,  -6.779999  ,   9.059998  ],
#         [ -8.68      ,   2.2200012 ,  18.059998  ],
#         ...,
#         [ -2.6800003 ,   5.220001  ,   7.0599976 ],
#         [ 12.32      ,  23.220001  ,  24.059998  ],
#         [ 29.32      ,  44.22      ,  42.059998  ]],
#
#        [[-30.68      , -20.779999  ,  -2.9400024 ],
#         [-42.68      , -32.78      , -14.940002  ],
#         [ -4.6800003 ,   6.220001  ,  23.059998  ],
#         ...,
#         [ 19.32      ,  27.220001  ,  25.059998  ],
#         [ 43.32      ,  54.22      ,  50.059998  ],
#         [ 77.32      ,  90.22      ,  87.06      ]],
#
#        [[-18.68      ,  -6.779999  ,  11.059998  ],
#         [-10.68      ,   0.22000122,  18.059998  ],
#         [ -7.6800003 ,   2.2200012 ,  20.059998  ],
#         ...,
#         [ 44.32      ,  52.22      ,  47.059998  ],
#         [ 64.32      ,  73.22      ,  68.06      ],
#         [ 30.32      ,  39.22      ,  37.059998  ]],
#
#        ...,
#
#        [[  2.3199997 ,   2.2200012 ,   7.0599976 ],
#         [  6.3199997 ,   5.220001  ,  10.059998  ],
#         [  6.3199997 ,   5.220001  ,  10.059998  ],
#         ...,
#         [ 19.32      ,  25.220001  ,  28.059998  ],
#         [ 23.32      ,  27.220001  ,  32.059998  ],
#         [ 21.32      ,  24.220001  ,  29.059998  ]]]], dtype=float32)}
# 
       # print("results:")
       # print(self.sess.run(self.outputs, feed_dict=feed))
       #   results:
       #   [array([286])]


