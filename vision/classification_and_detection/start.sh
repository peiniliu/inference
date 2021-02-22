export MODEL_DIR=/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/models
export DATA_DIR=/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/test_imagenet
#export DATA_DIR=/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/fake_imagenet
#export DATA_DIR=/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/data_imagenet


# Notes:
# run_local $1 backend $2 model $3 device $4 extra_args
#  -- run_common $profile=resnet50-mlflow/mobilenet-tf 
#                $model_path=$MODEL_DIR/resnet50_v1.pb

#./run_local.sh onnxruntime mobilenet cpu --accuracy
#./run_local.sh onnxruntime mobilenet cpu --scenario Offline
#./run_local.sh tf resnet50 cpu --scenario Offline
#./run_local.sh tf resnet50 cpu --scenario Server --count 2
#./run_local.sh tfserving resnet50 cpu --scenario SingleStream --count 2 --server 172.30.0.50:31930
#./run_local.sh tfserving resnet50 cpu --scenario MultiStream --count 2 --server 172.30.0.50:31930
#./run_local.sh tfserving resnet50 cpu --scenario Server --count 2 --server 172.30.0.50:31930
./run_local.sh tfserving resnet50 cpu --scenario Offline --count 2 --server 172.30.0.50:31930
