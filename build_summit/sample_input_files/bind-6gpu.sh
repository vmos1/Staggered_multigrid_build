#!/bin/bash
# Evan Weinberg, evansweinberg@gmail.com
# Binding script for 6 GPUs per node. Based on a script given to me by Kate, which I believe was based on something from Steve, which may have been based on something originally by Kate...

lrank=$(($PMIX_RANK % 6))
echo "PMIX_RANK is", $PMIX_RANK
echo "lrank is $lrank"

echo $APP

case ${lrank} in
 [0])
 export PAMI_IBV_DEVICE_NAME=mlx5_0:1
 numactl --physcpubind=0,4,8,12,16,20,24 --membind=0 $APP
 ;;
 
 [1])
 export PAMI_IBV_DEVICE_NAME=mlx5_0:1
 numactl --physcpubind=28,32,36,40,44,48,52 --membind=0 $APP
 ;;
 
 [2])
 export PAMI_IBV_DEVICE_NAME=mlx5_0:1
 numactl --physcpubind=56,60,64,68,72,76,80 --membind=0 $APP
 ;;
 
 [3])
 export PAMI_IBV_DEVICE_NAME=mlx5_3:1
 numactl --physcpubind=88,92,96,100,104,108,112 --membind=8 $APP
 ;;
 
 [4])
 export PAMI_IBV_DEVICE_NAME=mlx5_3:1
 numactl --physcpubind=116,120,124,128,132,136,140 --membind=8 $APP
 ;;
 
 [5])
 export PAMI_IBV_DEVICE_NAME=mlx5_3:1
 numactl --physcpubind=144,148,152,156,160,164,168 --membind=8 $APP
 ;;
esac
