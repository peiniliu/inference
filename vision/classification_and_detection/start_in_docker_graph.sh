#setup loadgen
#cd /root/loadgen
#CFLAGS="-std=c++14" python setup.py develop
#pip install mlflow
#pip install seldon-core

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

#./run_local.sh tfserving resnet50 cpu --scenario SingleStream --count 2 --server resnet-service.resnet-tf:8500
#./run_local.sh tfserving resnet50 cpu --scenario MultiStream --count 2 --server 172.30.0.50:31930
#./run_local.sh tfserving resnet50 cpu --scenario Server --count 2 --server 172.30.0.50:31930
#./run_local.sh tfserving resnet50 cpu --scenario Offline --count 20 --server resnet-service.resnet-tf:8500

#data imagenet
#./run_local.sh tfserving resnet50 cpu --scenario SingleStream --count 2 --server resnet-service.resnet-tf:8500
./run_local.sh seldon resnet50 cpu --scenario Offline --server 10.108.184.226:15101

