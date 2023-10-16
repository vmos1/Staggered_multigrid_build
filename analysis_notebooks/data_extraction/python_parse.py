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


def f_extract(fname,run_type,m_light=3,m_multi=7,m_heavy=10):
    '''
    Extract Multigrid and solver Solver info from MILC output file
    m_light -> Number of lightest masses for MG or CG 
    m_multi -> Number of light masses for multishift CG
    m_heavy -> Number of heavy quark masses
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
    for count in range(m_light):
        key='mass-{:02d}'.format(count+1)
        dict1[key]=np.nan
    
    if run_type in ['mg']: 

        # Extract set of lines of the form : 'CONGRAD5: time = 1.313335e+03 (fn_QUDA_MG D) masses = 1 iters = 7 mflops = 6.297085'
        op=f_grep_exec('fn_QUDA_MG D',fname)

        # For 3 light masses: 
        # mass-01 : # rows 0,3,6,9,12,15. subtract setup time from row 0
        # mass-02 # rows 1,4,7,10,13,16
        # ...
        # Factor of 6 = 3 colors * 2 for odd-even
        
        for count in range(m_light): # Iterate over light mass index
            row_range=range(count,m_light*6,m_light)    
            tme=0.0

            for row in row_range:
                if row==0: ## First row has setup time included so subtract it out
                    val=float(op[row].split(' (fn_QUDA_MG D)')[0].split('time = ')[-1]) - dict1['mg-setup']
                elif row!=0:
                    val=float(op[row].split(' (fn_QUDA_MG D)')[0].split('time = ')[-1])
                tme+=val
            dict1['mass-{:02d}'.format(count+1)]=tme/2.0

    elif run_type in ['cg_split']: 

        # Extract set of lines of the form : 'CONGRAD5: time = 1.561823e+01 (fn_QUDA D) masses = 1 iters = 7104 mflops = 5.373881e+05'
        op=f_grep_exec('fn_QUDA D',fname)
        # First 18 lines for light quark, next 60 lines for heavy quark, then 18 again for light and 60 again for heavy
        ## CG gives separate lines for even and odd, so there are 6 lines for each

        # Drop the lines for heavy quarks(60 lines each time)
        idx_list=list(range( 6*m_light)) + list(range(6* m_heavy+ 6*m_light,6* m_heavy +6*m_light +6*m_light))
        op=[op[i] for i in idx_list]
        print(len(op))
        
        # For 3 light masses,
        # First 6 lines for m01, next 6 lines for m02 ...     After m_light x 6, second source
        # Factor of 6 = 3 colors * 2 for odd-even
        # mass-01 : # rows 0-5, 18-24 
        # mass-02 : # rows 6-12, 24-30 ...
        
        for count in range(m_light): # Iterate over light mass index
            start1=6*count
            start2=m_light*6 + (count*6)

            row_range=list(range(start1, start1+6)) + list(range(start2, start2+6))
            tme=0.0

            for row in row_range:
                val=float(op[row].split(' (fn_QUDA D)')[0].split('time = ')[-1])
                tme+=val
            dict1['mass-{:02d}'.format(count+1)]=tme/2.0
    
    ### multishift cg for lighter masses
    if m_multi: # Only if multi-shift CG masses are present
        op=f_grep_exec('multicg_offset_QUDA D',fname)  
        # Extract time = {} in string : 'CONGRAD5: time = 1.967970e+01 (multicg_offset_QUDA D) masses = 7 iters = 6148 mflops = 4.073360e+05'
        dict1['mass_multi']=sum([float(i.split(' (multicg')[0].split('time = ')[-1]) for i in op])/2
    else: dict1['mass_multi']=0.0
    
    ### Heavy quark masses
    op=f_grep_exec('fn_QUDA D',fname)
    # Extract time = {} in string : 'CONGRAD5: time = 1.441724e+00 (fn_QUDA D) masses = 1 iters = 500 mflops = 4.097366e+05'
    
    if run_type=='cg_split': # cg_split also writes light masses as fn_QUDA, so drop those lines

        # For 3 light masses, drop 0-18, 
        start1=m_light*6 
        start2=m_heavy*6 + m_light*6 + m_light*6
        idx_list=list(range(start1, start1 + m_heavy * 6)) + list(range(start2,start2+m_heavy*6))
        
        # idx_list=list(range(18,18+60)) + list(range(78+18,78+18+60))
        op=[op[i] for i in idx_list]
        
    dict1['mass-{:02d}-{:02d}'.format(m_light+m_multi+1,m_light+m_multi+m_heavy)]=sum([float(i.split(' (fn_QUDA')[0].split('time = ')[-1]) for i in op])/2

    key_multishift = 'mass-{:02d}-{:02d}'.format(m_light+1,m_light+m_multi) # eg: mass 04-10 

    if run_type in ['mg','cg_split']:
        if m_multi:
            dict1[key_multishift]=dict1['mass_multi']
            # dict1['mass-01-10']= sum([dict1[key] for key in ['mass-01','mass-02','mass-03','mass-04-10']])
        
        key_list=['mass-{:02d}'.format(count) for count in range(1,m_light+1)] # keys for all light masses
        if m_multi: key_list.append(key_multishift)

        dict1['mass-01-{:02d}'.format(m_light+m_multi)]= sum([dict1[key] for key in key_list])
    
    elif run_type=='cg':
        dict1['mass-01-{:02d}'.format(m_light+m_multi)]=dict1['mass_multi']
        dict1[key_multishift]=np.nan

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
        
        key_list=['mass-{:02d}'.format(count) for count in range(1,m_light+1)] # keys for all light masses
        if m_multi: key_list.append(key_multishift)
        key_list.append('mass-{:02d}-{:02d}'.format(m_light+m_multi+1,m_light+m_multi+m_heavy))
        
        dict1['solve-time']= sum([dict1[key] for key in key_list]) * 2.0

    elif run_type=='cg':
        dict1['solve-time'] = ( dict1['mass-01-{:02d}'.format(m_light+m_multi)] + dict1['mass-{:02d}-{:02d}'.format(m_light+m_multi+1,m_light+m_multi+m_heavy)] ) * 2.0

    # summed-time = solve-time + make/save-src + contractions + startup + loading  + mg-setup 
    dict1['summed-time'] = sum([ dict1[key] for key in ['startup','loading','mg-setup','solve-time','make/save-src','contractions']])

    # error = milc-total-time - summed-time 
    dict1['error'] = dict1['milc-total-time'] - dict1['summed-time']

    del dict1['mass_multi']
    
    return dict1

    
def f_print_dict(dict1,m_light=3,m_multi=7,m_heavy=10):
    '''
    print dictionary with specific order 
    '''
    list2=[ 'mg-setup', 'solve-time',\
              'startup', 'loading', 'mg-setup', 'make/save-src', 'contractions', 'quda-total-time', 'milc-total-time', 'solve-time', 'summed-time', 'error']

    
    key_list=['mass-{:02d}'.format(count) for count in range(1,m_light+1)] # keys for all light masses

    key_multishift = 'mass-{:02d}-{:02d}'.format(m_light+1,m_light+m_multi) # eg: mass 04-10 
    if m_multi: key_list.append(key_multishift)

    key_list.append('mass-{:02d}-{:02d}'.format(m_light+m_multi+1,m_light+m_multi+m_heavy))
    
    for i in list2:
        key_list.append(i)
                     
    print(key_list)
    for key in key_list:
        print(key,dict1[key])


 
if __name__=="__main__":

    f1='/ccs/home/venkitesh/mg_output_files/output-cg_144_crusher.kpp'
    f2='/ccs/home/venkitesh/mg_output_files/output-full_2_readingNN.kpp'
    # f3='/ccs/home/venkitesh/mg_output_files/output-cg_144_frontier_aug_2023.kpp'
    f3='/ccs/home/venkitesh/mg_output_files/output-cg_10split.kpp'

#     fname=f2
#     run_type='mg'
#     print(run_type,fname)
#     # dict1={}
#     dict1= f_extract(fname,run_type,m_light=3)
#     f_print_dict(dict1,m_light=3)
#     print("\n")
    
#     fname=f1
#     run_type='cg'
#     print(run_type,fname)
#     dict1={}
#     dict1= f_extract(fname,run_type,m_light=3)
#     f_print_dict(dict1,m_light=3)
    
    fname=f3
    run_type='cg_split'
    print(run_type,fname)
    dict1={}
    dict1= f_extract(fname,run_type,m_light=10,m_multi=0,m_heavy=10)
    f_print_dict(dict1,m_light=10)