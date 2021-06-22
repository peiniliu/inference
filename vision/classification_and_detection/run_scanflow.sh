#!/bin/bash

#predictor
./main.sh --dataset imagenet_tflocal --dataset-path test_imagenet --scenario Offline --model model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2 

#preprocessing
./main.sh --dataset imagenet_tflocal_preprocess --dataset-path test_imagenet --scenario Offline --model /model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2 --preprocess 1 
./main.sh --dataset imagenet_tflocal_preprocess --dataset-path test_imagenet --scenario Offline --model /gpfs/bsc_home/xpliu/pv/jupyterhubpeini/scanflow/tutorials/mlperf/model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2 --preprocess 2 
