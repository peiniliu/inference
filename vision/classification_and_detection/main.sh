#!/bin/bash

common_opt="--mlperf_conf ../../mlperf.conf"

echo "parameter $common_opt $# $*"
python python/main.py $common_opt $*
