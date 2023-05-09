#!/bin/bash

#SBATCH -A PHY157-ecphisq
#SBATCH -J QudaStagMG
#SBATCH -o %x-%j.out
#SBATCH -t 03:00:00
#SBATCH -N 288
#SBATCH -C nvme
#SBATCH --cpus-per-task=7
#SBATCH --ntasks-per-node=8

nodes=288
source ${BUILD_DIR}/install_scripts/setup_env_crusher.sh

executable=${BUILD_DIR}/milc_qcd/ks_spectrum/ks_spectrum_hisq
input=input-full.kpp
output=output-full.kpp

node_geom="4 6 6 16"
io_geom="${node_geom}"
runargs="-qmp-geom ${node_geom} -qmp-alloc-map 3 2 1 0 -qmp-logic-map 3 2 1 0"

export QUDA_RESOURCE_PATH=$PWD/tunecache # location of QUDA tunecache file
mkdir -p $QUDA_RESOURCE_PATH
export QUDA_ENABLE_GDR=1
export QUDA_MILC_HISQ_RECONSTRUCT=13
export QUDA_MILC_HISQ_RECONSTRUCT_SLOPPY=9

#export QUDA_ENABLE_DEVICE_MEMORY_POOL=0
#export QUDA_ENABLE_MANAGED_MEMORY=1
#export QUDA_ENABLE_MANAGED_PREFETCH=1

echo "START_RUN: `date`" >> $output
echo "EXECUTABLE =  $executable" >> $output
ls -l $executable >> $output
echo "RUNARGS = $runargs" >> $output

#export OMP_NUM_THREADS=7
export MPICH_ENV_DISPLAY=1
export MPICH_GPU_SUPPORT_ENABLED=1
export MPICH_SMP_SINGLE_COPY_MODE=XPMEM
export MPICH_COLL_SYNC=MPI_Bcast
export MPICH_OFI_NIC_VERBOSE=2

export APP="$executable $runargs $input $output"
echo ${APP} >> ${output}

export QUDA_RESOURCE_PATH=${PROGDIR}
export QUDA_PROFILE_OUTPUT_BASE=profile_64

##
export GPUDIRECT=" -gpudirect "
export MPICH_OFI_NIC_POLICY=NUMA
export FI_MR_CACHE_MAX_COUNT=0

# New vars
rm -f ./core
ulimit -c unlimited 
export OMP_NUM_THREADS=7
export OMP_PROC_BIND=spread
MASK_0="0x00fe000000000000"
MASK_1="0xfe00000000000000"
MASK_2="0x0000000000fe0000"
MASK_3="0x00000000fe000000"
MASK_4="0x00000000000000fe"
MASK_5="0x000000000000fe00"
MASK_6="0x000000fe00000000"
MASK_7="0x0000fe0000000000"
MEMBIND="--mem-bind=map_mem:3,3,1,1,0,0,2,2"
CPU_MASK="--cpu-bind=mask_cpu:${MASK_0},${MASK_1},${MASK_2},${MASK_3},${MASK_4},${MASK_5},${MASK_6},${MASK_7}"

cmd="srun -n $((nodes*8)) -N $nodes --ntasks-per-node=8 --cpus-per-task=7 ${CPU_MASK} ${MEMBIND} ${APP}"

echo COMMAND: $cmd >> $output
$cmd
echo "FINISH_RUN: `date`" >> $output

