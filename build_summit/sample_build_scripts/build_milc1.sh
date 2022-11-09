#!/bin/bash
#############
WORKDIR=/gpfs/alpine/lgt104/proj-shared/ayyar/builds_summit/install_nov9_2022

#############
## Source environment
source ${WORKDIR}/install_scripts/setup_env_summit.sh

############
## Build QUDA
QUDA_SRC=${WORKDIR}/QUDA/src/quda
QUDA_BUILD=${WORKDIR}/QUDA/build

MILCDIR=${WORKDIR}/MILC/milc_qcd
pushd .
git clone --branch develop https://github.com/lattice/quda $QUDA_SRC 
