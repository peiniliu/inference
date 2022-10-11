#!/bin/bash
if [ "$#" -ne 7 ]; then
        echo "missing parameters"
        echo "1 kubelet env [none,cpumem]"
        echo "2 benchmark [resnet]"
        echo "3 number of containers [1 2 4 8 16 32]"
        echo "4 server batch [128]"
        echo "5 client scenario [SS MS S O]"
        echo "6 client batch [2 4 8 16 32]"
        echo "7 rep"
        exit 1
fi

K8S_ENV=$1
bench=$2
num_container=$3
server_batch=$4
LIST_CLIENT_SCENARIOS=$5
LIST_CLIENT_BATCH=$6
REP=$7

echo "parameter run_test: $1 $2 $3 $4 $5 $6 $7"

OUTPUT_DIR="output-exp22"

#for k in `seq $REP` 
for k in $REP 
do
  for scen in $LIST_CLIENT_SCENARIOS
  do
     echo "$scen"
     case $scen in 
       "O")
         echo "scenario: offline"
         for c_batch in $LIST_CLIENT_BATCH
         do
              echo "output: $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k"
              /gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_tfserving --dataset-path data_imagenet --scenario Offline --model-name resnet50 --server 172.30.0.50:31930 --backend tfserving --output $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k --threads 72
              #mkdir $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k
              #for c in `seq 1`
              #do
              #  if [ $c == 1 ]
              #  then
              #    /gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_tfserving --dataset-path data_imagenet --scenario Offline --model-name resnet50 --server 172.30.0.50:31930 --backend tfserving --output $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k-$c --threads 36 --max-batchsize $c_batch
              #  else
              #    /gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_tfserving --dataset-path data_imagenet --scenario Offline --model-name resnet50 --server 172.30.0.50:31930 --backend tfserving --output $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k-$c --threads 36 --max-batchsize $c_batch &
              #  fi  
              #    #/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_tfserving --dataset-path data_imagenet --scenario Offline --model-name resnet50 --server 172.30.0.50:31930 --backend tfserving --output test --threads 36 --max-batchsize 8
              #done
              #sleep 30
              #mv -r $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k-* $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k
         done
         ;;
       "S")
         for c_batch in $LIST_CLIENT_BATCH
         do
            echo "output: $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k"
            /gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_tfserving --dataset-path data_imagenet --scenario Server --model-name resnet50 --server 172.30.0.50:31930 --backend tfserving --output $OUTPUT_DIR/$K8S_ENV-$bench-$num_container-$server_batch-$scen-$c_batch-$k 
         done
         ;;
       "SS")
         echo "SS not ready"
         ;;
       "MS")
         echo "MS not ready"
         ;;
       esac
  done
done
