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
./run_local.sh tf resnet50 cpu --scenario Offline 
