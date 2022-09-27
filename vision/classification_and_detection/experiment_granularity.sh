if [ "$#" -ne 7 ]; then
        echo "missing parameters"
        echo "1 kubelet env [none,cpumem]"
        echo "2 client scenario [SS MS S O]"
        echo "3 benchmark [resnet]"
        echo "4 number of containers [1 2 4 8 16 32]"
        echo "5 client batch [2 4 8 16 32]"
        echo "6 server batch [128]"
        echo "7 rep"
        echo "sh experiment_granularity.sh \"none cpumem\" \"S O\" \"resnet\" \"1 2 4 8 16 32\" \"2 4 6 8 10\" \"128\" 10"
        exit 1
fi

LIST_ENVS=$1
LIST_CLIENT_SCENARIOS=$2
LIST_BENCHMARKS=$3
LIST_NUM_CTNS=$4
LIST_CLIENT_BATCH=$5
LIST_SERVER_BATCH=$6
REP=$7

num_cpu=32
num_memory=128

echo "$1 $2 $3 $4 $5 $6 $7"

WORKDIR="/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection"


function change_k8s_env () {
  cd /gpfs/bsc_home/xpliu/k8s-ansible
  cp roles/node/templates/kubelet-config.yml.j2.$1 roles/node/templates/kubelet-config.yml.j2
  sudo ansible-playbook -i inventory/hosts  site.yml -t node
  cd $WORKDIR
}

#$1 bench $2 num_ctn $3 inter
function create_tfserving_service () {
  #sudo /usr/local/bin/kubectl apply -f $WORKDIR/performanceanalysis/yaml/$1_$2.yaml -n scanflow-ai-pa
  
  cpus=$(( $num_cpu / $2 ))
  memory=$(( $num_memory / $2 ))Gi
  num_inter=$3
  num_intra=2
  inter=$(( $num_inter / $2 ))
  #inter=$2
  intra=$(( $num_intra / $2 ))

  echo "num_ctn: $2 cpu: $cpus memory: $memory inter: $inter intra: $intra"

  cat <<EOF | sudo /usr/local/bin/kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resnet-deployment-$2
  namespace: scanflow-ai-pa
spec:
  selector:
    matchLabels:
      app: resnet-server
  replicas: $2
  template:
    metadata:
      labels:
        app: resnet-server
    spec:
      containers:
      - name: resnet-container
        image: 172.30.0.49:5000/tfserving
        args: ["--rest_api_num_threads=32","--tensorflow_intra_op_parallelism=$intra","--tensorflow_inter_op_parallelism=$inter"]
        env:
        - name: MODEL_NAME
          value: "$1"
        volumeMounts:
        - mountPath: /gpfs/bsc_home/xpliu/tensorboard
          name: log
        resources:
          limits:
            cpu: $cpus
            memory: $memory 
          requests:
            cpu: $cpus
            memory: $memory
        ports:
        - containerPort: 8500
          name: grpc
        - containerPort: 8501
          name: rest
      volumes:
      - name: log
        hostPath:
          path: /gpfs/bsc_home/xpliu/tensorboard
          type: DirectoryOrCreate
EOF

  sleep 60
}

function delete_tfserving_service () {
  sudo /usr/local/bin/kubectl delete -n scanflow-ai-pa deployments.apps $1-deployment-$2
  sleep 60
}

function change_affinity () {
  echo "changeaff: $1 $2"
  if [ $1 == "none" ]
  then
    echo "none"
    #ssh -o StrictHostKeyChecking=no nxt2026 "sudo sh /gpfs/bsc_home/xpliu/cpuset.sh 1 2-9,18-25"
    ssh -o StrictHostKeyChecking=no nxt2026 "sudo sh /gpfs/bsc_home/xpliu/cpuset.sh 1 2-17,20-35"
  elif [ $1 == "cpumemory" ]
  then
    echo "cpumemory"
    if [ $2 == 1 ]
    then
       echo "ctn1 does not change memory affinity"
    else
       ssh -o StrictHostKeyChecking=no nxt2026 "sudo sh /gpfs/bsc_home/xpliu/cpumem.sh 1"
    fi
  else
    echo "cpumem"
  fi
}

for K8S_ENV in $LIST_ENVS
do 
    #change_k8s_env $K8S_ENV
    for bench in $LIST_BENCHMARKS
    do
        #server setting
        for container in $LIST_NUM_CTNS
        do
            for batch in $LIST_SERVER_BATCH
            do 
                create_tfserving_service $bench $container $batch
                change_affinity $K8S_ENV $container
                echo "exp: $K8S_ENV $bench $container $batch \"$LIST_CLIENT_SCENARIOS\" \"$LIST_CLIENT_BATCH\" $REP"
                sh run_test.sh $K8S_ENV $bench $container $batch "$LIST_CLIENT_SCENARIOS" "$LIST_CLIENT_BATCH" $REP
                delete_tfserving_service $bench $container
            done 
        done
    done
done