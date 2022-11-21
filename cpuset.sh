option=$1
cpus=$2

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
        echo "change affinity"
        /bin/echo $cpus > $docker/cpuset.cpus
        cat $docker/cpuset.cpus
      fi
    else
      cat $docker/cpuset.cpus
      cat $docker/cpuset.mems
    fi
  done
  
  if [ $option == 1 ] 
  then
    #echo $cpus > $entry/cpuset.cpus
    cat $entry/cpuset.cpus
    cat $entry/cpuset.mems
  else
    cat $entry/cpuset.cpus
    cat $entry/cpuset.mems
  fi
done


if [ $option == 1 ] 
then
  #echo $cpus > $search_dir/cpuset.cpus
  #echo 1 > $search_dir/cpuset.cpu_exclusive
  cat $search_dir/cpuset.cpus
  cat $search_dir/cpuset.mems
else
  cat $search_dir/cpuset.cpus
  cat $search_dir/cpuset.mems
fi
