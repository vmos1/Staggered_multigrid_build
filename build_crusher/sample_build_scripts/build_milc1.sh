#!/bin/bash
#############
## Source environment
script_loc=/gpfs/alpine/lgt104/proj-shared/ayyar/builds_crusher/install_oct17_2022/install_scripts
source $script_loc/setup_env_crusher.sh

#git clone --branch feature/staggMG https://github.com/weinbe2/milc_qcd ${TOPDIR_HIP}/milc_qcd
git clone --branch develop https://github.com/milc-qcd/milc_qcd ${TOPDIR_HIP}/milc_qcd
