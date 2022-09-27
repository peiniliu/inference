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

echo "$1 $2 $3 $4 $5 $6 $7"

WORKDIR="/gpfs/bsc_home/xpliu/inference/vision/classification_and_detection/output-exp2"

#1.benchmark, 2.env
function create_head () {
        output="${1}-${2}.csv"
        echo "benchmark,k8senv,sbatch,numctn,cscenario,cbatch,reps,qps,mean,p50,p80,p90,p95,p99,p999"  > $output
        echo "createhead $output"
}


function gather_csv () {
        bench=$1
        env=$2
        sbatch=$3
        ctn=$4
        rep=$5

        for scenario in $LIST_CLIENT_SCENARIOS
        do 
            case $scenario in
                 "O")
                    for cbatch in $LIST_CLIENT_BATCH
                    do
                         FILE="${env}-${bench}-${ctn}-${sbatch}-${scenario}-${cbatch}-${k}/results.json"
                         echo "openfile: $FILE"
                         qps=`grep \"qps $FILE | awk -F':' '{print $2}' | awk -F',' '{print $1}'`
                         mean=`grep \"mean\" $FILE | awk -F':' '{print $2}' | awk -F',' '{print $1}'`
                         p50=`grep \"50.0\" $FILE | awk -F':' '{print $2}' | awk -F',' '{print $1}'`
                         p80=`grep \"80.0\" $FILE | awk -F':' '{print $2}' | awk -F',' '{print $1}'`
                         p90=`grep \"90.0\" $FILE | awk -F':' '{print $2}' | awk -F',' '{print $1}'`
                         p95=`grep \"95.0\" $FILE | awk -F':' '{print $2}' | awk -F',' '{print $1}'`
                         p99=`grep \"99.0\" $FILE | awk -F':' '{print $2}' | awk -F',' '{print $1}'`
                         p999=`grep \"99.9\" $FILE | awk -F':' '{print $2}' | awk -F',' '{print $1}'`
                         echo "$bench,$env,$sbatch,$ctn,offline,$cbatch,$rep,$qps,$mean,$p50,$p80,$p90,$p95,$p99,$p999" >> $output
                    done
                 ;;
                 "S")
                         echo "S scenario not ready"
                 ;;
            esac
        done


}


for bench in $LIST_BENCHMARKS
do
for env in $LIST_ENVS
do
        create_head $bench $env
        for sbatch in $LIST_SERVER_BATCH
        do
                for ctn in $LIST_NUM_CTNS
                do
                        #for k in `seq $REP`
                        for k in $REP
                        do
                                gather_csv $bench $env $sbatch $ctn $k
                        done
                done
        done
done
done
