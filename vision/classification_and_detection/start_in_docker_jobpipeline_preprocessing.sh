#setup loadgen
cd /root/loadgen
CFLAGS="-std=c++14" python setup.py develop
pip install mlflow

WORKDIR=/root/vision/classification_and_detection
cd $WORKDIR
export MODEL_DIR=$WORKDIR/models
#export DATA_DIR=$WORKDIR/test_imagenet
#export DATA_DIR=$WORKDIR/fake_imagenet
export DATA_DIR=$WORKDIR/data_imagenet


# Notes:
# run_local $1 backend $2 model $3 device $4 extra_args
#  -- run_common $profile=resnet50-mlflow/mobilenet-tf 
#                $model_path=$MODEL_DIR/resnet50_v1.pb


#batch
#./run_local.sh tf resnet50 cpu --scenario Offline 
source ./run_common.sh tf resnet50 cpu --scenario Offline

common_opt="--mlperf_conf ../../mlperf.conf"
dataset="--dataset-path $DATA_DIR"
OUTPUT_DIR=`pwd`/output/$name
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

python python/preprocessing.py --profile $profile $common_opt --model $model_path $dataset \
    --output $OUTPUT_DIR $EXTRA_OPS $@
