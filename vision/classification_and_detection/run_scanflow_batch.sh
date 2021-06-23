#!/bin/bash

#batch
#predictor
./main.sh --dataset imagenet_tflocal --dataset-path test_imagenet --scenario SingleStream --model model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2 
./main.sh --dataset imagenet_tflocal --dataset-path test_imagenet --scenario MultiStream --model model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2 
./main.sh --dataset imagenet_tflocal --dataset-path test_imagenet --scenario Server --model model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2 
./main.sh --dataset imagenet_tflocal --dataset-path test_imagenet --scenario Offline --model model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2 

#preprocessing
#./main.sh --dataset imagenet_tflocal --dataset-path test_imagenet --scenario Offline --model model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2 --preprocess 1 
#./main.sh --dataset imagenet_tflocal --dataset-path test_imagenet --scenario Offline --model model/0 --model-name resnet50 --inputs input_image --outputs predictions/Softmax:0 --backend tflocal --output output --count 2


