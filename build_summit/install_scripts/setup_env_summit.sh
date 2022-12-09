#!/bin/bash
#############

module purge
module load DefApps
module unload xalt/1.2.1
#module load cuda/11.3.1
module load cuda/11.0.3
#module load gcc/7.5.0
module load gcc/9.3.0
module load git/2.31.1
module load cmake/3.23.2
module load nsight-systems/2021.3.1.54
module load nsight-compute/2021.2.1
module load gdrcopy/2.2
module list


export LD_LIBRARY_PATH="$BUILD_DIR/QUDA/build/usqcd/lib:${LD_LIBRARY_PATH}"
