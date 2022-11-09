#!/bin/bash
#############
## Source environment

script_loc=/gpfs/alpine/lgt104/proj-shared/ayyar/builds_crusher/install_oct17_2022/install_scripts
source $script_loc/setup_env_crusher.sh
WORKDIR=$TOPDIR_HIP

############
## Build QUDA
QUDA_SRC=${WORKDIR}/QUDA/src/quda
QUDA_BUILD=${WORKDIR}/QUDA/build

pushd .
if [ ! -d $QUDA_SRC ]
then
##  git clone --branch feature/hip-compile-fixes https://github.com/lattice/quda $QUDA_SRC # clone QUDA to the desired directory
    git clone --branch develop https://github.com/lattice/quda $QUDA_SRC # clone QUDA to the desired directory
##    git clone --branch hotfix/gauge_path_test https://github.com/lattice/quda $QUDA_SRC # clone QUDA to the desired directory
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

export QUDA_GPU_ARCH=gfx90a

cd $QUDA_BUILD
cmake -DCMAKE_BUILD_TYPE=DEVEL -DQUDA_DIRAC_DEFAULT_OFF=ON -DQUDA_DIRAC_STAGGERED=ON -DQUDA_GAUGE_ALG=ON -DQUDA_GAUGE_TOOLS=ON -DQUDA_DOWNLOAD_USQCD=ON -DQUDA_QIO=ON -DQUDA_QMP=ON -DQUDA_MULTIGRID=ON -DQUDA_TARGET_TYPE="HIP" -DROCM_PATH=${ROCM_PATH} -DGPU_TARGETS="gfx90a" -DCMAKE_CXX_COMPILER="hipcc" -DCMAKE_C_COMPILER="hipcc" -DCMAKE_CXX_FLAGS="${MPI_CFLAGS}" -DCMAKE_C_FLAGS="${MPI_CFLAGS}" -DCMAKE_EXE_LINKER_FLAGS="${MPI_LDFLAGS}" -DCMAKE_SHARED_LINKER_FLAGS="${MPI_LDFLAGS}" -DCMAKE_C_STANDARD=99 -DCMAKE_INSTALL_PREFIX=${INSTALLROOT}/quda $QUDA_SRC

nice make VERBOSE=1 -j 16 
make install
popd
