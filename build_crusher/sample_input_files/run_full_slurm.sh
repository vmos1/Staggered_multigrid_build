#!/bin/bash 

#SBATCH -A lgt104_crusher
#SBATCH -J QudaStagMG
#SBATCH -o %x-%j.out
#SBATCH -t 02:00:00
#SBATCH -N 108
#SBATCH --cpus-per-task=8
#SBATCH --ntasks-per-node=8

nodes=108
source ${BUILD_DIR}/install_scripts/setup_env_crusher.sh

executable=${BUILD_DIR}/milc_qcd/ks_spectrum/ks_spectrum_hisq
input=input-full.kpp
output=output-full.kpp

node_geom="6 3 6 8"
io_geom="${node_geom}"
#runargs="-qmp-geom ${node_geom} -qmp-alloc-map 0 1 2 3 -qmp-logic-map 0 1 2 3"
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

export OMP_NUM_THREADS=8
export MPICH_ENV_DISPLAY=1
export MPICH_GPU_SUPPORT_ENABLED=1
export MPICH_SMP_SINGLE_COPY_MODE=XPMEM
export MPICH_COLL_SYNC=MPI_Bcast
export MPICH_OFI_NIC_VERBOSE=1

export APP="$executable $runargs $input $output"
echo ${APP} >> ${output}
cmd="srun -n $((nodes*8)) -N $nodes --unbuffered --gpus-per-node=8 --ntasks-per-node=8 --cpus-per-task=8 --distribution=*:block ${APP}"

echo COMMAND: $cmd >> $output
$cmd
echo "FINISH_RUN: `date`" >> $output

