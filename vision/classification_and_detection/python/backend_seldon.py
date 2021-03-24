"""
tf-seldon
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

from seldon_core.seldon_client import SeldonClient

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("BackendSeldon")


class BackendSeldon(backend.Backend):
    def __init__(self):
        super(BackendSeldon, self).__init__()

    def version(self):
        return tf.__version__ + "/" + tf.__git_version__

    def name(self):
        return "seldon"

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
            raise ValueError("BackendSeldon needs seldon running model")
        self.server = server
        self.outputs = outputs
        self.inputs = inputs

        #seldonclient
        self.sc = SeldonClient(deployment_name="image",namespace="resnet-tf-graph", \
                  gateway="istio", \
                  gateway_endpoint=server, payload_type='tftensor', transport="grpc", \
                  client_return_type="proto", \
                  grpc_max_send_message_length=419430400, grpc_max_receive_message_length=419430400)

        log.info("PEINI: seldon server is running")
        return self

    def predict(self, data):
        r = self.sc.predict(data=data)
        preds = tf.make_ndarray(r.response.data.tftensor)
        log.info("PEINI: number of response label {}".format(len(preds)))
        return preds


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


