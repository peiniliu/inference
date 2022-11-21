option=$1

echo " option : $option"
search_dir="/sys/fs/cgroup/cpuset/kubepods.slice"
#for entry in $search_dir/kubepods-pod*
for entry in $search_dir/kubepods-*
do
  echo "$entry"
    
  for docker in $entry/docker-*
  do
    echo "$docker"
    tasks=`cat "$docker/tasks" | wc -l`
    echo " tasks: $tasks"
    if [ $option == 1 ] 
    then
      if [ $tasks == "1" ]
      then
        #cat $docker/tasks
        cat $docker/cpuset.cpus
      else
        echo "change memory affinity"
        cpus=`cat "$docker/cpuset.cpus" | awk -F'-' '{print $1}'`
        if [[ $cpus -le 18 ]]
        then
          echo "node 0"
          /bin/echo 0 > $docker/cpuset.mems
        else
          echo "node 1"
          /bin/echo 1 > $docker/cpuset.mems
        fi
        cat $docker/cpuset.cpus
        cat $docker/cpuset.mems
      fi
    else
      cat $docker/cpuset.cpus
      cat $docker/cpuset.mems
    fi
  done
  
done
