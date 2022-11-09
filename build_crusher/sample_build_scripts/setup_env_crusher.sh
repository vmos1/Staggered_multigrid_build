#!/bin/bash
#############

module load craype-accel-amd-gfx90a
module load cray-mpich/8.1.12
module load cmake
module load rocm/4.5.2
module list

export MPICH_ROOT=/opt/cray/pe/mpich/8.1.12
export MPICH_DIR=${MPICH_ROOT}/ofi/crayclang/10.0

## These must be set before running

export TOPDIR_HIP=/gpfs/alpine/lgt104/proj-shared/ayyar/builds_crusher/install_oct17_2022

#export SRCROOT=${TOPDIR_HIP}/../src
#export BUILDROOT=${TOPDIR_HIP}/build
export INSTALLROOT=${TOPDIR_HIP}/install
export GPU_TARGET=gfx90a

MPI_CFLAGS="-I${MPICH_DIR}/include -g"
MPI_LDFLAGS="-g -L${MPICH_DIR}/lib -lmpi -L${MPICH_ROOT}/gtl/lib -lmpi_gtl_hsa"

export PK_BUILD_TYPE="Release"

export PATH=${ROCM_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${INSTALLROOT}/quda/lib:${MPICH_DIR}/lib:${MPICH_ROOT}/gtl/lib:${LD_LIBRARY_PATH}

