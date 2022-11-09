# Instructions for building Staggered Multigrid on Summit
We need to build QUDA and MILC in sequence.  QUDA can be built with a single script. Due to the need to edit some files in MILC after download, it is built in two steps.
The procedure is described below.
* **Generate build scripts**: You need a ```build_dir``` and ```run_dir```.
  - Use the jupyter notebook [build_summit/build_install_scripts_summit.ipynb](https://github.com/vmos1/Staggered_multigrid_build/blob/main/build_summit/build_install_scripts_summit.ipynb)
    - Edit the folder names in *dict_pars['build_dir']* and *dict_pars['run_dir']* to point to the appropriate locations for your run. 
    - Run the entire jupyter notebook. It will copy all install scripts to the desired location. \
  - Manually copy and edit scripts : 
      - Manually create empty directories inside ```build_dir``` as ``` mkdir QUDA/src install install_scripts```
      - Copy the contents of the folder *sample_install_scripts* to ```build_dir/install_scripts/```
      - Edit the contents of the files ```build_quda.sh```, ``` build_milc1.sh``` & ``` build_milc2.sh``` : Modify ```script_loc=<build_directory>/install_scripts```

* **Build instructions**: 
  - ```cd <build_dir>``` 
  - ```./install_scripts/build_quda.sh 2>&1 | tee op_quda.out ```
  - ```./install_scripts/build_milc1.sh 2>&1 | tee op_milc1.out ```
  - Make edits to files as listed below: 
In the file [milc_qcd/ks_spectrum/compile_ks_spectrum_hisq_quda.sh](https://github.com/milc-qcd/milc_qcd/blob/develop/ks_spectrum/compile_ks_spectrum_hisq_quda.sh), uncomment lines 42-45 for NVIDIA Gpus.
  - ```./install_scripts/build_milc2.sh 2>&1 | tee op_milc2.out ```

This should build both QUDA and MILC. 

# Instructions for running code

| Command | Description | 
| -- | -- |
| ```cd <run_dir>``` | Enter run directory |
| ```cp build_summit/sample_input_files/* .```  | Copy the input files from build_summit/sample_input_files to the required location |
| ```mkdir rand``` | Create directory for storing random numbers | 
| ```ln -s /gpfs/alpine/proj-shared/lgt104/detar/lat``` | Create sym link for gauge configuration | 
| Edit the `input*.kpp` and `mgparams*.txt` files | Edit for varying local volume, MG layers, etc. | 
| Edit the `run-mg-tune.lsf` and `run-mg-full.lsf` files | Add the correct location of the build directory for PROJ in line 15 |
| ```bsub run_tune_slurm.sh``` | Submit tuning run |
| ```bsub run_tune_slurm.sh``` | Submit full run | 











A sample build document is provided here. 
