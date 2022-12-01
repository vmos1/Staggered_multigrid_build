#!/bin/bash
date
#############
## Source environment
script_loc=$BUILD_DIR/install_scripts
source $script_loc/setup_env_crusher.sh

QUDA_INSTALL=${INSTALLROOT}/quda

LIBQUDA="-Wl,-rpath ${QUDA_INSTALL}/lib -L${QUDA_INSTALL}/lib -lquda -D__gfx90a --offload-arch=gfx90a --amdgpu-target=gfx90a -Wl,-rpath=${ROCM_PATH}/hiprand/lib -L${ROCM_PATH}/hiprand/lib -Wl,-rpath=${ROCM_PATH}/rocfft/lib -L${ROCM_PATH}/rocfft/lib -lhiprand -lrocfft -Wl,-rpath=${ROCM_PATH}/hipblas/lib -L${ROCM_PATH}/hipblas/lib -lhipblas -Wl,-rpath=${ROCM_PATH}/rocblas/lib -L${ROCM_PATH}/rocblas/lib -lrocblas -Wl,-rpath=${ROCM_PATH}/hip/lib"

echo $BUILD_DIR/milc_qcd/ks_spectrum
############ Make ks_spectrum_hisq ##################
cd $BUILD_DIR/milc_qcd/ks_spectrum
cp ../Makefile .
make clean

MY_CC=hipcc MY_CXX=hipcc ARCH="" COMPILER="gnu" OPT="-O3 --offload-arch=gfx90a" CUDA_HOME="" QUDA_HOME=${QUDA_INSTALL} WANTQUDA=true WANT_FN_CG_GPU=true WANT_FL_GPU=true WANT_GF_GPU=true WANT_FF_GPU=true WANT_MIXED_PRECISION_GPU=2 PRECISION=2 MPP=true OMP=true WANTQIO=true WANTQMP=true QIOPAR=${INSTALLROOT}/quda QMPPAR=${INSTALLROOT}/quda LIBQUDA=${LIBQUDA} OFFLOAD=HIP CGEOM="-DFIX_NODE_GEOM -DFIX_IONODE_GEOM" KSCGMULTI="-DKS_MULTICG=HYBRID -DMULTISOURCE -DMULTIGRID" CTIME="-DNERSC_TIME -DCGTIME -DFFTIME -DFLTIME -DGFTIME -DREMAP -DPRTIME -DIOTIME" make -j 1 ks_spectrum_hisq
cd ..

date
