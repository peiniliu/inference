
import os

import tensorflow as tf
from tensorflow import keras

print(tf.version.VERSION)

#mnist test
#import mlflow.keras
#
#model = tf.keras.models.load_model('/gpfs/bsc_home/xpliu/tensorflow-model/examples/vision/imageclassification/mnist/model/saved_model')
#model.summary()
#
## Log metrics and log the model
#with mlflow.start_run() as run:
#    mlflow.keras.log_model(model, "models")


#resnet test
import mlflow.keras
from tensorflow.keras.applications.resnet50 import ResNet50

model = ResNet50(weights='imagenet')
#model.save()

# Log metrics and log the model
with mlflow.start_run() as run:
    mlflow.keras.log_model(model, "models")



#import mlflow.tensorflow
#
#mlflow.tensorflow.autolog()
#mlflow.set_tracking_uri("http://172.30.0.49:5001")
#
## Log metrics and log the model
#with mlflow.start_run() as run:
#   #mlflow.tensorflow.log_model(model, "models")
#   model = tf.saved_model.load('/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/models/saved_model')
#   feat_specifications = {
#       "SepalLength": tf.Variable([], dtype=tf.float64, name="SepalLength"),
#       "SepalWidth": tf.Variable([], dtype=tf.float64, name="SepalWidth"),
#       "PetalLength": tf.Variable([], dtype=tf.float64, name="PetalLength"),
#       "PetalWidth": tf.Variable([], dtype=tf.float64, name="PetalWidth"),
#   }
#
#   receiver_fn = tf.estimator.export.build_raw_serving_input_receiver_fn(feat_specifications)
#   temp = "./"
#   # The model is automatically logged when export_saved_model() is called.
#   model.export_saved_model(temp, receiver_fn).decode("utf-8")
#
# 
