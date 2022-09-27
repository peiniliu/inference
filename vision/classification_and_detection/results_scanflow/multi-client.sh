#!/bin/bash

SCENARIO=$1
NUM_OF_CLIENT=100

for i in `seq $NUM_OF_CLIENT` 
do
    case $1 in
      "ss")
          /gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon_preprocessed --dataset-path data_imagenet --scenario SingleStream --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-graph --backend seldon --output ss_${i} --count 50 &
       ;;
      "s")
          /gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon_preprocessed --dataset-path data_imagenet --scenario Server --model-name resnet50 --server 172.30.0.50:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-single --backend seldon --output ss_${i} --max-latency 60 --count 1000 &
       ;;
     esac
done


