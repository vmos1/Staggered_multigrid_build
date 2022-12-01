#!/bin/bash
#############

## Source environment
source ${BUILD_DIR}/install_scripts/setup_env_summit.sh

############
## Build QUDA
QUDA_SRC=${BUILD_DIR}/QUDA/src/quda
QUDA_BUILD=${BUILD_DIR}/QUDA/build

MILCDIR=${BUILD_DIR}/MILC/milc_qcd
pushd .
git clone --branch develop https://github.com/lattice/quda $QUDA_SRC 
