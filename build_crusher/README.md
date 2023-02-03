# Instructions for building and running Staggered Multigrid on Crusher and Frontier supercomputers
We need to build QUDA and MILC in sequence.  QUDA and MILC can each be built with a single script. 
The procedure is described below.
## **Generate build scripts**: 
You need 2 directories: ```build_dir``` and ```run_dir```.
- **Using the python script**  :
  - Run the script [build_crusher/build_install_scripts.py](https://github.com/vmos1/Staggered_multigrid_build/blob/main/build_crusher/build_install_scripts.py) as 
  
  `python build_install_scripts.py --machine crusher -bdir <build_dir>`. 
  - It will create <build_dir> and copy all install scripts to the desired location in `build_dir`.

 **OR Alternatively**  
- **Manually copy and edit scripts** : 

| Command | Description | 
| -- | -- |
| `export BUILD_DIR=<build_dir>`| Setup paths |
| `cd $BUILD_DIR` | Enter build directory |
| ` mkdir QUDA/src install` | Manually create 2 empty directories inside `build_dir`  |
| `cp -r <repo_dir>/build_crusher/install_scripts $BUILD_DIR/` | Copy the folder [*build_crusher/install_scripts*](https://github.com/vmos1/Staggered_multigrid_build/tree/main/build_crusher/install_scripts) to `<build_dir>/` |

## **Build instructions**: 
  - ```cd <build_dir>``` 
  - `export BUILD_DIR=$PWD`
  - `./install_scripts/build_quda.sh 2>&1 | tee op_quda.out `
  - `./install_scripts/build_milc.sh 2>&1 | tee op_milc.out `

This should build both QUDA and MILC. 

## Instructions for running Staggered Multigrid on crusher

| Command | Description | 
| -- | -- |
| ```cd <run_dir>``` | Enter run directory |
| ```cp <repo_dir>/build_crusher/sample_input_files/* .```  | Copy the input files from [build_crusher/sample_input_files](https://github.com/vmos1/Staggered_multigrid_build/tree/main/build_crusher/sample_input_files) to the required location |
| ```mkdir rand``` | Create directory for storing random numbers | 
| ```ln -s /gpfs/alpine/proj-shared/lgt104/detar/lat``` | Create sym link for gauge configuration | 
| Edit the `input*.kpp` and `mgparams*.txt` files | Edit for varying local volume, MG layers, etc. | 
| `export BUILD_DIR=<build_dir>`| Setup build path |
| ```sbatch run_tune_slurm.sh``` | Submit tuning run |
| ```sbatch run_full_slurm.sh``` | Submit full run after completion of tuning run | 

