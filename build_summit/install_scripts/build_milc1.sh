#!/bin/bash
#############

## Source environment
script_loc=$BUILD_DIR/install_scripts
source $script_loc/setup_env_summit.sh

############
## Build QUDA
git clone --branch develop https://github.com/milc-qcd/milc_qcd $BUILD_DIR/milc_qcd
