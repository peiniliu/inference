#!/bin/bash

SCENARIO=$1
DIR=$2
NUM_OF_CLIENT=20


RESULTS_HOME="/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/${DIR}"

output="${SCENARIO}-clients${NUM_OF_CLIENT}-${DIR}.csv"
echo "clients,senario,min,max,mean,50,90,95,97,99,99.9"  >> $output
echo "createhead $output"


for i in `seq $NUM_OF_CLIENT` 
do
    case $1 in
      "ss")
          mean=`grep "Mean latency (ns)               :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}'`
          min=`grep "Min latency (ns)                :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}'`
          max=`grep "Max latency (ns)                :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}'`
          latency50th=`grep "50.00 percentile latency (ns)   :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}' `
          latency90th=`grep "90.00 percentile latency (ns)   :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}' `
          latency95th=`grep "95.00 percentile latency (ns)   :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}' `
          latency97th=`grep "97.00 percentile latency (ns)   :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}' `
          latency99th=`grep "99.00 percentile latency (ns)   :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}' `
          latency999th=`grep "99.90 percentile latency (ns)   :" ${RESULTS_HOME}/ss_${i}/mlperf_log_summary.txt |awk -F':' '{print $2}' `
          echo "${i},${SCENARIO},${min},${max},${mean},${latency50th},${latency90th},${latency95th},${latency97th},${latency99th},${latency999th}"  >> $output
       ;;
      "s")
          /gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/main.sh --dataset imagenet_seldon --dataset-path data_imagenet --scenario Server --model-name resnet50 --server 172.30.0.58:40000 --namespace scanflow-mlperf-dataengineer --deployment_name online-inference-graph --backend seldon --output output --max-latency 60 --count 1000
       ;;
     esac
done


