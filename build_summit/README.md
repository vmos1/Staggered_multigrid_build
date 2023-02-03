# Instructions for building and running Staggered Multigrid on Summit
We need to build QUDA and MILC in sequence.  QUDA and MILC can each be built with a single script.
The procedure is described below.
## **Generate build scripts**: 
You need 2 directories: ```build_dir``` and ```run_dir```.
- **Using the python script**  :
  - Run the script [build_summit/build_install_scripts_summit.py](https://github.com/vmos1/Staggered_multigrid_build/blob/main/build_summit/build_install_scripts_summit.py) as `python build_install_scripts_summit.py -bdir <build_dir>`. 
  - It will create <build_dir> and copy all install scripts to the desired location in `build_dir`.

 **OR Alternatively**  
- **Manually copy and edit scripts** : 

| Command | Description | 
| -- | -- |
| `export BUILD_DIR=<build_dir>`| Setup paths |
| `cd $BUILD_DIR` | Enter build directory |
| ` mkdir QUDA/src install install_scripts` | Manually create 3 empty directories inside `build_dir`  |
| `cp -r <repo_dir>/build_summit/install_scripts $BUILD_DIR/` | Copy the folder [*build_summit/install_scripts*](https://github.com/vmos1/Staggered_multigrid_build/tree/main/build_summit/install_scripts) to `<build_dir>/` |


## **Build instructions**: 
  - ```cd <build_dir>``` 
  - `export BUILD_DIR=$PWD`
  - ```./install_scripts/build_quda.sh 2>&1 | tee op_quda.out ```
  - ```./install_scripts/build_milc.sh 2>&1 | tee op_milc.out ```


This should build both QUDA and MILC. 

## Instructions for running code on Summit

| Command | Description | 
| -- | -- |
| ```cd <run_dir>``` | Enter run directory |
| ```cp <repo_dir>/build_summit/sample_input_files/* .```  | Copy the input files from [build_summit/sample_input_files](https://github.com/vmos1/Staggered_multigrid_build/tree/main/build_summit/sample_input_files) to the required location |
| ```mkdir rand``` | Create directory for storing random numbers | 
| ```ln -s /gpfs/alpine/proj-shared/lgt104/detar/lat``` | Create sym link for gauge configuration | 
| Edit the `input*.kpp` and `mgparams*.txt` files | Edit for varying local volume, MG layers, etc. | 
| `export BUILD_DIR=<build_dir>`| Setup build path |
| ```bsub run-mg-tune.lsf``` | Submit tuning run |
| ```bsub run-mg-full.lsf``` | Submit full run after completion of tuning run | 

