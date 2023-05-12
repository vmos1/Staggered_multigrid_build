#!/bin/bash
#############

module load cmake
module load cpe/23.03
module load craype-accel-amd-gfx90a
module load PrgEnv-amd
module load amd/5.4.3
module load cray-mpich/8.1.25
module load gcc-mixed/12.2.0

module list

export MPICH_ROOT=/opt/cray/pe/mpich/8.1.25
export MPICH_ROOT=/opt/cray/pe/mpich/8.1.25
export GTL_ROOT=/opt/cray/pe/mpich/8.1.25/gtl/lib
export MPICH_DIR=${MPICH_ROOT}/ofi/amd/5.0
 
MPI_CFLAGS="${CRAY_XPMEM_INCLUDE_OPTS} -I${MPICH_DIR}/include "
MPI_LDFLAGS="L/opt/cray/libfabric/1.15.0.0/lib64  -Wl,-rpath=/opt/cray/libfabric/1.15.0.0/lib64 ${CRAY_XPMEM_POST_LINK_OPTS} -lxpmem  -Wl,-rpath=${MPICH_DIR}/lib -L${MPICH_DIR}/lib -lmpi -Wl,-rpath=${GTL_ROOT} -L${GTL_ROOT} -lmpi_gtl_hsa -L${ROCM_PATH}/llvm/lib
-Wl,-rpath=${ROCM_PATH}/llvm/lib"

## These must be set before running
export INSTALLROOT=${BUILD_DIR}/install
export GPU_TARGET=gfx90a

MPI_CFLAGS="-I${MPICH_DIR}/include -g"
MPI_LDFLAGS="-g -L${MPICH_DIR}/lib -lmpi -L${MPICH_ROOT}/gtl/lib -lmpi_gtl_hsa"

export PK_BUILD_TYPE="Release"

export PATH=${ROCM_PATH}/bin:${PATH}
export LD_LIBRARY_PATH=${INSTALLROOT}/quda/lib:${MPICH_DIR}/lib:${MPICH_ROOT}/gtl/lib:${LD_LIBRARY_PATH}

    
