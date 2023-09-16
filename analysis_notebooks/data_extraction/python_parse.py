# Parse MILC output to get Multigrid info
# Sept 14, 2023
import os, glob
import subprocess as sp
import numpy as np
import pandas as pd

### Modules 
def f_grep_exec(grep_strg,fname):
    '''
    Use grep with string to extract from a file
    '''
    
    cmd="grep '%s' %s"%(grep_strg,fname)
    op=sp.check_output(cmd,shell=True).decode().split('\n') # decode bytes to string and split by newlines
    op=[i for i in op if i] # Drop null string      
    return op



def f_extract(fname,run_type):
    '''
    Extract Multigrid and solver Solver info from MILC output file
    '''
    
    dict1={}
    assert run_type in ['mg','cg','cg_split'], "run_type not recognized: must be either 'mg', 'cg' or 'cg_split'"
    
    op=f_grep_exec('Aggregate time to setup',fname)  
    dict1['startup']=float(op[0].split(' ')[-1])

    op=f_grep_exec('Aggregate time to readin',fname)  
    dict1['loading']=float(op[0].split(' ')[-1])

    if run_type in ['mg']: 
        # Extract the line 'mat_invert_mg_field_gpu: MG inverter setup complete. Time = <..>'
        op=f_grep_exec('MG inverter setup complete',fname)
        dict1['mg-setup']=float(op[0].split(' ')[-1])

    elif run_type in ['cg','cg_split'] : dict1['mg-setup']=0.0


    # Extract light masses 

    for key in ['mass-01','mass-02','mass-03']: dict1[key]=np.nan
    
    if run_type in ['mg']: 

        # Extract set of lines of the form : 'CONGRAD5: time = 1.313335e+03 (fn_QUDA_MG D) masses = 1 iters = 7 mflops = 6.297085'
        op=f_grep_exec('fn_QUDA_MG D',fname)

        # mass-01
        tme=0.0
        row_range=range(0,18,3) # rows 0,3,6,9,12,15
        for row in row_range:
            if row==0: ## First row has setup time included so subtract it out
                val=float(op[row].split(' (fn_QUDA_MG D)')[0].split('time = ')[-1]) - dict1['mg-setup']
            elif row!=0: 
                val=float(op[row].split(' (fn_QUDA_MG D)')[0].split('time = ')[-1])
            tme+=val
        dict1['mass-01']=tme/2.0

        # mass-02
        tme=0.0
        row_range=range(1,18,3) # rows 1,4,7,10,13,16
        for row in row_range:
            val=float(op[row].split(' (fn_QUDA_MG D)')[0].split('time = ')[-1])
            tme+=val
        dict1['mass-02']=tme/2.0

        # mass-03
        tme=0.0
        row_range=range(2,18,3) # rows 2,5,8,11,14,17
        for row in row_range:
            val=float(op[row].split(' (fn_QUDA_MG D)')[0].split('time = ')[-1])
            tme+=val
        dict1['mass-03']=tme/2.0
        
        
    elif run_type in ['cg_split']: 

        # Extract set of lines of the form : 'CONGRAD5: time = 1.561823e+01 (fn_QUDA D) masses = 1 iters = 7104 mflops = 5.373881e+05'
        op=f_grep_exec('fn_QUDA D',fname)
        # First 18 lines for light quark, next 60 lines for heavy quark, then 18 again for light and 60 again for heavy
        
        idx_list=list(range(18)) + list(range(60+18,60+18+18))
        op=[op[i] for i in idx_list]
        
        print(len(op))

        # mass-01
        tme=0.0
        row_range=list(range(0,6)) + list(range(18,24)) # rows 0-5, 18-72
        for row in row_range:
            val=float(op[row].split(' (fn_QUDA D)')[0].split('time = ')[-1])
            tme+=val
        dict1['mass-01']=tme/2.0/2.0 # Extra factor of 2 due to double CG calc !!!
        
        # mass-02
        tme=0.0
        row_range= list(range(6,12)) + list(range(24,30))
        for row in row_range:
            val=float(op[row].split(' (fn_QUDA D)')[0].split('time = ')[-1])
            tme+=val
        dict1['mass-02']=tme/2.0/2.0

        # mass-03
        tme=0.0
        row_range=list(range(12,18))  + list(range(30,36))
        for row in row_range:
            val=float(op[row].split(' (fn_QUDA D)')[0].split('time = ')[-1])
            tme+=val
        dict1['mass-03']=tme/2.0/2.0

    ### multishift cg for 7 lighter masses
    op=f_grep_exec('multicg_offset_QUDA D',fname)  
    # Extract time = {} in string : 'CONGRAD5: time = 1.967970e+01 (multicg_offset_QUDA D) masses = 7 iters = 6148 mflops = 4.073360e+05'
    dict1['mass_multi']=sum([float(i.split(' (multicg')[0].split('time = ')[-1]) for i in op])/2

    ### 10 heavy quark masses
    op=f_grep_exec('fn_QUDA D',fname)
    # Extract time = {} in string : 'CONGRAD5: time = 1.441724e+00 (fn_QUDA D) masses = 1 iters = 500 mflops = 4.097366e+05'
    
    if run_type=='cg_split': # cg_split also writes light masses as fn_QUDA, so drop those lines
        idx_list=list(range(18,18+60)) + list(range(78+18,78+18+60))
        op=[op[i] for i in idx_list]
        
    dict1['mass-11-20']=sum([float(i.split(' (fn_QUDA')[0].split('time = ')[-1]) for i in op])/2

    if run_type in ['mg','cg_split']:
        dict1['mass-04-10']=dict1['mass_multi']
        dict1['mass-01-10']= sum([dict1[key] for key in ['mass-01','mass-02','mass-03','mass-04-10']])
    elif run_type=='cg':
        dict1['mass-01-10']=dict1['mass_multi']
        dict1['mass-04-10']=np.nan

    # make/save-src
    op=f_grep_exec('Aggregate time to create sources',fname)
    dict1['make/save-src']=float(op[0].split(' ')[-1])

    op=f_grep_exec('Aggregate time to tie meson correlators',fname)
    dict1['contractions']=float(op[0].split(' ')[-1])

    op=f_grep_exec('QUDA Total time',fname)
    # # remove string 'secs' from the end
    dict1['quda-total-time']=op[0].split(' time =  ')[-1].split(' secs')[0] 

    op=f_grep_exec('Time = .* seconds',fname)
    # # MILC total time is the line with seconds at the end. remove string 'seconds' from the end
    dict1['milc-total-time']=float(op[0].split('Time = ')[-1].split(' seconds')[0])

    # solve-time  = ( mass-01 - mass-10 + mass 11-20 ) x 2 
    if run_type in ['mg','cg_split']:
        dict1['solve-time'] = ( dict1['mass-01'] + dict1['mass-02'] + dict1['mass-03'] + dict1['mass-04-10'] + dict1['mass-11-20'] ) * 2.0
    elif run_type=='cg':
        dict1['solve-time'] = ( dict1['mass-01-10'] + dict1['mass-11-20'] ) * 2.0

    # summed-time = solve-time + make/save-src + contractions + startup + loading  + mg-setup 
    dict1['summed-time'] = sum([ dict1[key] for key in ['startup','loading','mg-setup','solve-time','make/save-src','contractions']])

    # error = milc-total-time - summed-time 
    dict1['error'] = dict1['milc-total-time'] - dict1['summed-time']

    del dict1['mass_multi']
    
    return dict1


def f_print_dict(dict1):
    '''
    print dictionary with specific order 
    '''
    key_list=[ 'mg-setup', 'mass-01','mass-02','mass-03', 'mass-01-10', 'mass-04-10', 'mass-11-20', 'solve-time',\
              'startup', 'loading', 'mg-setup', 'make/save-src', 'contractions', 'quda-total-time', 'milc-total-time', 'solve-time', 'summed-time', 'error']

    for key in key_list:
        print(key,dict1[key])

 
        
if __name__=="__main__":

    f1='/ccs/home/venkitesh/mg_output_files/output-cg_144_crusher.kpp'
    f2='/ccs/home/venkitesh/mg_output_files/output-full_2_readingNN.kpp'

    fname=f2
    run_type='mg'
    print(run_type,fname)
    dict1={}
    dict1= f_extract(fname,run_type)
    f_print_dict(dict1)
    print("\n")
    
    fname=f1
    run_type='cg'
    print(run_type,fname)
    dict1={}
    dict1= f_extract(fname,run_type)
    f_print_dict(dict1)