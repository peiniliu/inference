#!/bin/bash

#online
#single
#/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon_preprocessed --dataset-path test_imagenet --scenario SingleStream --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-single --backend seldon --output output --count 2 
#/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon_preprocessed --dataset-path test_imagenet --scenario MultiStream --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-single --backend seldon --output output --count 2 
#/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon_preprocessed --dataset-path test_imagenet --scenario Server --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-single --backend seldon --output output --count 2 
#/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon_preprocessed --dataset-path test_imagenet --scenario Offline --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --max-batchsize 4 --deployment_name online-inference-single --backend seldon --output output --count 2 

#graph
/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon --dataset-path data_imagenet --scenario Offline --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --max-batchsize 4 --deployment_name online-inference-graph --backend seldon --output output
#/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon --dataset-path test_imagenet --scenario SingleStream --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-graph --backend seldon --output output --count 2 
#/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon --dataset-path test_imagenet --scenario MultiStream --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-graph --backend seldon --output output --count 2 
#/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon --dataset-path test_imagenet --scenario Server --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-graph --backend seldon --output output --count 2 
#/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon --dataset-path test_imagenet --scenario Offline --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --max-batchsize 4 --deployment_name online-inference-graph --backend seldon --output output --count 2 


