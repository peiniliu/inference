option=$1
cpus=$2

echo " option : $option"
/bin/echo off > /sys/devices/system/cpu/smt/control

for cpu in `seq $cpus`
do
  echo "$(( $cpu - 1))"
    if [ $option == 1 ] 
    then
        echo "change freq"
        /bin/echo performance > /sys/devices/system/cpu/cpu$(( $cpu - 1 ))/cpufreq/scaling_governor
    fi
done


if [ $option == 1 ] 
then
  cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
fi
