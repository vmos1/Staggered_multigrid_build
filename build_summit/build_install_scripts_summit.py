# Script to generate scripts for buildig QUDA and MILC for Staggered Multigrid on the Summit supercomputer.
## Example run: python build_install_scripts.py -bdir temp/temp2
'''Code does the following: 
Creates parent directory
3 directories install, install_scripts, QUDA/src
creates 3 files setup_env.sh, build_quda.sh, build_milc.sh and copies them to install_scripts
'''

import os
import subprocess as sp
import argparse
import shutil

def f_parse_args():
    """Parse command line arguments.Only for .py file"""
    parser = argparse.ArgumentParser(description="Script to generate scripts for buildig QUDA and MILC for Staggered Multigrid on Summit supercomputer", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_arg = parser.add_argument
    
    add_arg('--machine','-m', type=str, choices=['summit'], default='summit', help='Machine used')
    add_arg('--build_dir','-bdir', type=str, default='', help='build directory')
    
    return parser.parse_args()


def f_build_env_script(dict_pars,fname):
    
    env_strg='''#!/bin/bash
#############

module purge
module load DefApps
module unload xalt/1.2.1
module load cuda/{cuda}
module load gcc/9.3.0
module load git/2.31.1
module load cmake/3.23.2
module load nsight-systems/2021.3.1.54
module load nsight-compute/2021.2.1
module load gdrcopy/2.2
module list

export LD_LIBRARY_PATH="${{BUILD_DIR}}/QUDA/build/usqcd/lib:${{LD_LIBRARY_PATH}}"
'''.format(**dict_pars)

    with open(fname,'w') as f: f.write(env_strg)


def f_build_quda_script(dict_pars,fname):
    
    quda_strg='''#!/bin/bash
date
#############
## Source environment
source ${{BUILD_DIR}}/install_scripts/setup_env.sh

############
## Build QUDA
QUDA_SRC=${{BUILD_DIR}}/QUDA/src/quda
QUDA_BUILD=${{BUILD_DIR}}/QUDA/build

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
'''.format(**dict_pars)
    
    with open(fname,'w') as f: f.write(quda_strg)


def f_build_milc_script(dict_pars,fname):

    milc_strg='''#!/bin/bash
#############

## Source environment
script_loc=$BUILD_DIR/install_scripts
source $script_loc/setup_env.sh

############
## Build MILC
git clone --branch develop https://github.com/milc-qcd/milc_qcd $BUILD_DIR/milc_qcd
### Uncomment specific lines from the file milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh 
## for NVIDIA GPUs uncomment lines 42-45
sed -i "42 s/#//" milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh;
sed -i "43 s/#//" milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh;
sed -i "44 s/#//" milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh;
sed -i "45 s/#//" milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh;

############
QUDA_SRC=${{BUILD_DIR}}/QUDA/src/quda
QUDA_BUILD=${{BUILD_DIR}}/QUDA/build

## Build MILC

MILCDIR=${{BUILD_DIR}}/milc_qcd

cd ${{MILCDIR}}/ks_spectrum && cp ${{MILCDIR}}/Makefile ${{MILCDIR}}/ks_spectrum
export PATH_TO_CUDA=/sw/summit/cuda/{cuda}
export USQCD_BUILD=${{QUDA_BUILD}}/usqcd

PATH_TO_CUDA=$PATH_TO_CUDA PATH_TO_QUDA=$QUDA_BUILD PATH_TO_QMP=$USQCD_BUILD PATH_TO_QIO=$USQCD_BUILD POWER9=1 MULTIGRID=1 $MILCDIR/ks_spectrum/./compile_ks_spectrum_hisq_quda.sh

cd $BUILD_DIR
date

'''.format(**dict_pars)
    
    
    with open(fname,'w') as f: f.write(milc_strg)
    

if __name__=="__main__":
    args=f_parse_args()
         
    if args.build_dir=='':     args.build_dir=os.getcwd()+'/new_runs_1'
    print("Build scripts for ",args.machine)
    print("Build directory: ",args.build_dir)
    
    dict_pars={}
    dict_pars['build_dir']= args.build_dir
    dict_pars['machine']  = args.machine
    
    ## Define cuda version to use in setupfile
    dict_pars['cuda']='11.0.3'
    
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
        # os.rename(fname,dict_pars['build_dir']+'/install_scripts/'+fname)
        shutil.move(fname,dict_pars['build_dir']+'/install_scripts/'+fname)
    
