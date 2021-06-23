#!/bin/bash

#online
#single
./main.sh --dataset imagenet_seldon_preprocessed --dataset-path test_imagenet --scenario Server --model-name resnet50 --server 10.108.184.226:15101 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-single --backend seldon --output output --count 2 

#graph
#./main.sh --dataset imagenet_seldon --dataset-path test_imagenet --scenario Offline --model-name resnet50 --server 10.108.184.226:15101 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-graph --backend seldon --output output --count 2 


