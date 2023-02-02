# Script to generate scripts for buildig QUDA and MILC for Staggered Multigrid on Summit, Crusher and Frontier supercomputers
## Example run: python build_install_scripts.py --machine frontier -bdir temp/temp2


import os
import subprocess as sp
import argparse


def f_parse_args():
    """Parse command line arguments.Only for .py file"""
    parser = argparse.ArgumentParser(description="Script to generate scripts for buildig QUDA and MILC for Staggered Multigrid on Summit, Crusher and Frontier supercomputers", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_arg = parser.add_argument
    
    add_arg('--machine','-m', type=str, choices=['summit','crusher','frontier'], default='crusher', help='Machine used')
    add_arg('--build_dir','-bdir', type=str, default='', help='build directory')
    
    return parser.parse_args()




def f_build_env_script(dict_pars,fname):
    
    ### Setup env
    env_strg='''#!/bin/bash
#############

module load craype-accel-amd-gfx90a
module load cray-mpich/8.1.14
module load cmake
module load rocm/4.5.2
module list

export MPICH_ROOT=/opt/cray/pe/mpich/8.1.14
export MPICH_DIR=${{MPICH_ROOT}}/ofi/crayclang/10.0

## These must be set before running

#export SRCROOT=${{BUILD_DIR}}/../src
#export BUILDROOT=${{BUILD_DIR}}/build
export INSTALLROOT=${{BUILD_DIR}}/install
export GPU_TARGET=gfx90a

MPI_CFLAGS="-I${{MPICH_DIR}}/include -g"
MPI_LDFLAGS="-g -L${{MPICH_DIR}}/lib -lmpi -L${{MPICH_ROOT}}/gtl/lib -lmpi_gtl_hsa"

export PK_BUILD_TYPE="Release"

export PATH=${{ROCM_PATH}}/bin:${{PATH}}
export LD_LIBRARY_PATH=${{INSTALLROOT}}/quda/lib:${{MPICH_DIR}}/lib:${{MPICH_ROOT}}/gtl/lib:${{LD_LIBRARY_PATH}}

    '''.format(**dict_pars)

    with open(fname,'w') as f: f.write(env_strg)


def f_build_quda_script(dict_pars,fname):
    
    quda_strg='''#!/bin/bash
date
#############
## Source environment

script_loc=$BUILD_DIR/install_scripts
source $script_loc/setup_env.sh
WORKDIR=$BUILD_DIR

############
## Build QUDA
QUDA_SRC=${{WORKDIR}}/QUDA/src/quda
QUDA_BUILD=${{WORKDIR}}/QUDA/build

pushd .
if [ ! -d $QUDA_SRC ]
then
##  git clone --branch feature/hip-compile-fixes https://github.com/lattice/quda $QUDA_SRC # clone QUDA to the desired directory
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

export QUDA_GPU_ARCH=gfx90a

cd $QUDA_BUILD
cmake -DCMAKE_BUILD_TYPE=DEVEL -DQUDA_DIRAC_DEFAULT_OFF=ON -DQUDA_DIRAC_STAGGERED=ON -DQUDA_GAUGE_ALG=ON -DQUDA_GAUGE_TOOLS=ON -DQUDA_DOWNLOAD_USQCD=ON -DQUDA_QIO=ON -DQUDA_QMP=ON -DQUDA_MULTIGRID=ON \
-DQUDA_MULTIGRID_NVEC_LIST="6,24,48,64,96" \
-DQUDA_TARGET_TYPE="HIP" \
-DROCM_PATH=${{ROCM_PATH}} \
-DGPU_TARGETS="gfx90a" \
-DCMAKE_CXX_COMPILER="hipcc" \
-DCMAKE_C_COMPILER="hipcc" \
-DCMAKE_CXX_FLAGS="${{MPI_CFLAGS}}" \
-DCMAKE_C_FLAGS="${{MPI_CFLAGS}}" \
-DCMAKE_EXE_LINKER_FLAGS="${{MPI_LDFLAGS}}" \
-DCMAKE_SHARED_LINKER_FLAGS="${{MPI_LDFLAGS}}" \
-DCMAKE_C_STANDARD=99 \
-DCMAKE_INSTALL_PREFIX=${{INSTALLROOT}}/quda \
$QUDA_SRC

nice make VERBOSE=1 -j 16 
make install
popd

date
'''.format(**dict_pars)

    with open(fname,'w') as f: f.write(quda_strg)


def f_build_milc_script(dict_pars,fname):

    milc_strg1='''#!/bin/bash
#############
## Source environment
script_loc=$BUILD_DIR/install_scripts
source $script_loc/setup_env.sh

##git clone --branch feature/staggMG https://github.com/weinbe2/milc_qcd ${{BUILD_DIR}}/milc_qcd
git clone --branch develop https://github.com/milc-qcd/milc_qcd ${{BUILD_DIR}}/milc_qcd


### Uncomment specific lines from the file milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh 
## for all GPUs line 45
sed -i "45 s/#//" milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh;

'''.format(**dict_pars)
    
    
    ## Exception for NVIDIA GPUs
    if dict_pars['machine']=='summit':
        milc_strg1+='## for NVIDIA GPUs also uncomment lines 42-44'
        milc_strg1+='\nsed -i "42 s/#//" milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh;'
        milc_strg1+='\nsed -i "43 s/#//" milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh;'
        milc_strg1+='\nsed -i "44 s/#//" milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh;\n\n'
    
    milc_strg2='''QUDA_INSTALL=${{INSTALLROOT}}/quda

LIBQUDA="-Wl,-rpath ${{QUDA_INSTALL}}/lib -L${{QUDA_INSTALL}}/lib -lquda -D__gfx90a --offload-arch=gfx90a --amdgpu-target=gfx90a -Wl,-rpath=${{ROCM_PATH}}/hiprand/lib -L${{ROCM_PATH}}/hiprand/lib -Wl,-rpath=${{ROCM_PATH}}/rocfft/lib -L${{ROCM_PATH}}/rocfft/lib -lhiprand -lrocfft -Wl,-rpath=${{ROCM_PATH}}/hipblas/lib -L${{ROCM_PATH}}/hipblas/lib -lhipblas -Wl,-rpath=${{ROCM_PATH}}/rocblas/lib -L${{ROCM_PATH}}/rocblas/lib -lrocblas -Wl,-rpath=${{ROCM_PATH}}/hip/lib"

echo $BUILD_DIR/milc_qcd/ks_spectrum
############ Make ks_spectrum_hisq ##################
cd $BUILD_DIR/milc_qcd/ks_spectrum
cp ../Makefile .
make clean

MY_CC=hipcc \
MY_CXX=hipcc \
ARCH="" \
COMPILER="gnu" \
OPT="-O3 --offload-arch=gfx90a" \
CUDA_HOME="" \
QUDA_HOME=${{QUDA_INSTALL}} \
WANTQUDA=true \
WANT_FN_CG_GPU=true \
WANT_FL_GPU=true \
WANT_GF_GPU=true \
WANT_FF_GPU=true \
WANT_MIXED_PRECISION_GPU=2 \
PRECISION=2 \
MPP=true \
OMP=true \
WANTQIO=true \
WANTQMP=true \
QIOPAR=${{INSTALLROOT}}/quda \
QMPPAR=${{INSTALLROOT}}/quda \
LIBQUDA=${{LIBQUDA}} \
OFFLOAD=HIP \
CGEOM="-DFIX_NODE_GEOM -DFIX_IONODE_GEOM" \
KSCGMULTI="-DKS_MULTICG=HYBRID -DMULTISOURCE -DMULTIGRID" \
CTIME="-DNERSC_TIME -DCGTIME -DFFTIME -DFLTIME -DGFTIME -DREMAP -DPRTIME -DIOTIME" \
make -j 1 ks_spectrum_hisq
cd ..

date
'''.format(**dict_pars)
    
    milc_strg=milc_strg1+milc_strg2
    
    with open(fname,'w') as f: f.write(milc_strg)
    
    

if __name__=="__main__":
    args=f_parse_args()
         
    if args.build_dir=='':     args.build_dir=os.getcwd()
    print("Build scripts for ",args.machine)
    print("Build directory: ",args.build_dir)
    
    dict_pars={}
    dict_pars['build_dir']= args.build_dir
    dict_pars['machine']  = args.machine
    
    # Create empty directories
    
    ## Create upper level directories
    if os.path.exists(dict_pars['build_dir']):
        print('Error: Directory '+dict_pars['build_dir']+' exists')
        print("Please delete the directory or give a different build location")
        raise SystemExit
    else:
        os.makedirs(dict_pars['build_dir']+'/QUDA/src/')
        os.makedirs(dict_pars['build_dir']+'/install')
        os.makedirs(dict_pars['build_dir']+'/install_scripts')
    
    # Build scripts depending on machine
    fname1='setup_env.sh'
    fname2='build_quda.sh'
    fname3='build_milc.sh'
    f_build_env_script(dict_pars,fname1)
    f_build_quda_script(dict_pars,fname2)
    f_build_milc_script(dict_pars,fname3)
    
    # Write files
    print("Copying scripts to ",args.build_dir+'/install_scripts')
    for fname in [fname1,fname2,fname3]: 
        
        # make executables
        
        cmd='chmod +x {0}'.format(fname)
        op=sp.check_output(cmd,shell=True)
        # print(op)
        
        # move files to location

        # print(fname,dict_pars['build_dir']+'/install_scripts/'+fname)
        os.rename(fname,dict_pars['build_dir']+'/install_scripts/'+fname)
    
    # Move files
    
    