# Instructions for building and running Staggered Multigrid on Crusher
We need to build QUDA and MILC in sequence.  QUDA can be built with a single script. Due to the need to edit some files in MILC after download, it is built in two steps.
The procedure is described below.
## **Generate build scripts**: 
You need 2 directories: ```build_dir``` and ```run_dir```.
- **Using the jupyter notebook**  :
  - Edit the folder names in `dict_pars['build_dir']` and `dict_pars['run_dir']` to point to the appropriate locations.
  - Run the entire jupyter notebook [build_crusher/build_install_scripts_crusher.ipynb](https://github.com/vmos1/Staggered_multigrid_build/blob/main/build_crusher/build_install_scripts_crusher.ipynb). It will copy all install scripts to the desired location in `build_dir`.

 **OR Alternatively**  
- **Manually copy and edit scripts** : 

| Command | Description | 
| -- | -- |
| `export BUILD_DIR=<build_dir>`| Setup paths |
| `cd $BUILD_DIR` | Enter build directory |
| ` mkdir QUDA/src install install_scripts` | Manually create empty directories inside `build_dir`  |
| `cp -r <repo_dir>/build_crusher/install_scripts $BUILD_DIR/` | Copy the folder [*build_crusher/install_scripts*](https://github.com/vmos1/Staggered_multigrid_build/tree/main/build_crusher/install_scripts) to `<build_dir>/` |

## **Build instructions**: 
  - ```cd <build_dir>``` 
  - `export BUILD_DIR=$PWD`
  - `./install_scripts/build_quda.sh 2>&1 | tee op_quda.out `
  - `./install_scripts/build_milc1.sh 2>&1 | tee op_milc1.out `
  - Make edits to files as listed below: 
    - In the file [milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh](https://github.com/milc-qcd/milc_qcd/blob/develop/ks_spectrum/compile_ks_spectrum_hisq_quda.sh), uncomment lines 45 (for non-NVIDIA GPUs).
  - ```./install_scripts/build_milc2.sh 2>&1 | tee op_milc2.out ```

This should build both QUDA and MILC. 

## Instructions for running Staggered Multigrid on Crusher

| Command | Description | 
| -- | -- |
| ```cd <run_dir>``` | Enter run directory |
| `export BUILD_DIR=<build_dir>`| Setup build path |
| ```cp <repo_dir>/build_crusher/sample_input_files/* .```  | Copy the input files from [build_crusher/sample_input_files](https://github.com/vmos1/Staggered_multigrid_build/tree/main/build_crusher/sample_input_files) to the required location |
| ```mkdir rand``` | Create directory for storing random numbers | 
| ```ln -s /gpfs/alpine/proj-shared/lgt104/detar/lat``` | Create sym link for gauge configuration | 
| Edit the `input*.kpp` and `mgparams*.txt` files | Edit for varying local volume, MG layers, etc. | 
| ```sbatch run_tune_slurm.sh``` | Submit tuning run |
| ```sbatch run_full_slurm.sh``` | Submit full run after completion of tuning run | 

