#!/bin/bash
date
#############
## Source environment
source ${BUILD_DIR}/install_scripts/setup_env.sh

############
## Build QUDA
QUDA_SRC=${BUILD_DIR}/QUDA/src/quda
QUDA_BUILD=${BUILD_DIR}/QUDA/build

pushd .
if [ ! -d $QUDA_SRC ]
then
  git clone --branch develop https://github.com/lattice/quda $QUDA_SRC # clone QUDA to the desired directory
else
  cd $QUDA_SRC; git pull; cd ..
fi

if [ ! -d $QUDA_BUILD ]
then
  mkdir $QUDA_BUILD
else
  cd $QUDA_BUILD
  rm -rf *
fi

cd $QUDA_BUILD
cmake -DCMAKE_BUILD_TYPE=RELEASE -DQUDA_DIRAC_DEFAULT_OFF=ON -DQUDA_DIRAC_STAGGERED=ON -DQUDA_GPU_ARCH=sm_70 -DQUDA_DOWNLOAD_USQCD=ON -DQUDA_QIO=ON -DQUDA_QMP=ON -DQUDA_MULTIGRID=ON -DQUDA_MULTIGRID_NVEC_LIST    ="24,64,96" $QUDA_SRC
nice make -j 4
make install
popd

date
