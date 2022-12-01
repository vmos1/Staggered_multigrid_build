#!/bin/bash
date

#############
## Source environment
script_loc=$BUILD_DIR/install_scripts
source $script_loc/setup_env_summit.sh

############
## Build QUDA
QUDA_SRC=${BUILD_DIR}/QUDA/src/quda
QUDA_BUILD=${BUILD_DIR}/QUDA/build

## Build MILC

MILCDIR=${BUILD_DIR}/milc_qcd

cd ${MILCDIR}/ks_spectrum && cp ${MILCDIR}/Makefile ${MILCDIR}/ks_spectrum
export PATH_TO_CUDA=/sw/summit/cuda/11.0.3 # NEED TO MAKE THIS MORE ROBUST TO DIFFERENT CUDA VERSIONS, ASSUMES 11.0.3
export USQCD_BUILD=${QUDA_BUILD}/usqcd

PATH_TO_CUDA=$PATH_TO_CUDA PATH_TO_QUDA=$QUDA_BUILD PATH_TO_QMP=$USQCD_BUILD PATH_TO_QIO=$USQCD_BUILD POWER9=1 MULTIGRID=1 $MILCDIR/ks_spectrum/./compile_ks_spectrum_hisq_quda.sh

cd $BUILD_DIR
date
