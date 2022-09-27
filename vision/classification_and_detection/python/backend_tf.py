"""
tensorflow backend (https://github.com/tensorflow/tensorflow)
"""

# pylint: disable=unused-argument,missing-docstring,useless-super-delegation

import tensorflow as tf
from tensorflow.core.framework import graph_pb2

import backend

class BackendTensorflow(backend.Backend):
    def __init__(self):
        super(BackendTensorflow, self).__init__()

    def version(self):
        return tf.__version__ + "/" + tf.__git_version__

    def name(self):
        return "tensorflow"

    def image_format(self):
        # By default tensorflow uses NHWC (and the cpu implementation only does NHWC)
        return "NHWC"

    def load(self, model_path, inputs=None, outputs=None):
        # there is no input/output meta data i the graph so it need to come from config.
        if not inputs:
            raise ValueError("BackendTensorflow needs inputs")
        if not outputs:
            raise ValueError("BackendTensorflow needs outputs")
        self.outputs = outputs
        self.inputs = inputs

        print(tf.__version__)
        # physical_devices = tf.config.list_physical_devices('GPU')
        # try:
        #     # Disable first GPU
        #     tf.config.set_visible_devices(physical_devices[1:], 'GPU')
        #     logical_devices = tf.config.list_logical_devices('GPU')
        #     # Logical device was not created for first GPU
        #     assert len(logical_devices) == len(physical_devices) - 1
        # except:
        #     # Invalid device or cannot modify virtual devices once initialized.
        #     pass
        
        #config = tf.ConfigProto(device_count = {'CPU': 0})
        # # Set CPU as available physical device
        # my_devices = tf.config.experimental.list_physical_devices(device_type='CPU')
        # tf.config.experimental.set_visible_devices(devices= my_devices, device_type='CPU')

        # # To find out which devices your operations and tensors are assigned to
        # tf.debugging.set_log_device_placement(True)

        # # Create some tensors and perform an operation
        # a = tf.constant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        # b = tf.constant([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        # c = tf.matmul(a, b)

        # print(c)
        # physical_devices = tf.config.list_physical_devices('CPU')
        # print(physical_devices)
        # tf.config.set_visible_devices(physical_devices[0:], 'CPU')
        
        # print(tf.config.threading.get_inter_op_parallelism_threads())
        # print(tf.config.threading.get_intra_op_parallelism_threads())
        # tf.config.threading.set_inter_op_parallelism_threads(1)
        # tf.config.threading.set_intra_op_parallelism_threads(1)

        # TODO: support checkpoint and saved_model formats?
        graph_def = graph_pb2.GraphDef()
        print(dir(graph_def))
        with open(model_path, "rb") as f:
            graph_def.ParseFromString(f.read())
        g = tf.compat.v1.import_graph_def(graph_def, name='')
        print(dir(g))
        self.sess = tf.compat.v1.Session(graph=g)
        print(dir(self.sess))
        devices = self.sess.list_devices()
        for d in devices:
            print(d.name)
        return self

    def predict(self, feed):
        return self.sess.run(self.outputs, feed_dict=feed)
