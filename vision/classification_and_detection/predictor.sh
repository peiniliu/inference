#!/bin/bash

common_opt="--mlperf_conf ../../mlperf.conf"

#parameters
parameters=""

GETOPT_ARGS=`getopt -o d:p:s:c:r:m:n:i:o:b:a:w: -al dataset:,dataset-path:,scenario:,count:,preprocess:,model:,model-name:,inputs:,outputs:,backend:,cache_dir:,output: -- "$@"`
eval set -- "$GETOPT_ARGS"
#获取参数
while true;
do
        case "$1" in
                -d|--dataset) echo "$1" ; parameters="$parameters --dataset $2"; shift 2;;
                -p|--dataset-path) parameters="$parameters --dataset-path $2"; shift 2;;
                -s|--scenario) parameters="$parameters --scenario $2"; shift 2;;
                -c|--count) parameters="$parameters --count $2"; shift 2;;
                -r|--preprocess) parameters="$parameters --preprocess $2"; shift 2;;
                -m|--model) parameters="$parameters --model $2"; shift 2;;
                -n|--model-name) parameters="$parameters --model-name $2"; shift 2;;
                -i|--inputs) parameters="$parameters --inputs $2"; shift 2;;
                -o|--outputs) parameters="$parameters --outputs $2"; shift 2;;
                -b|--backend) parameters="$parameters --backend $2"; shift 2;;
                -a|--cache_dir) parameters="$parameters --cache_dir $2"; shift 2;;
                -w|--output) parameters="$parameters --output $2"; shift 2;;
                --) break ;;
                *) echo $parameters; break ;;
        esac
done

echo "parameter $common_opt $# "
echo "parameter args  $parameters"
python python/main.py $common_opt $parameters
