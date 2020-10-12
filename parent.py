# Launching script

import os
import subprocess
import time
from props import *
from numpy import *
from sympy import *
import pickle as pk
from ablation_base import vol
from ablation_base import pack
from ablation_base import temp_variation
#from ablation_base import pore_pressure

print('The analysis has just begun...')

# Temperature points for the analysis
tems=[300,325,350,375,400,425,450]
#tems=[475,500,525,550,575,600,625,650,675,700]
#tems=[650]
for tt in tems:
    mat_vol,pore_vol=vol(tt)
    print ('pore volume at this temperature is: ',pore_vol)
    pack(pore_vol,tt)
    temp_variation(tt)
    #p_tot=pore_pressure(tt)
    #print ('The total pore pressure in each pore is (Mpa): ',p_tot)

    # to check and see if the pores are big enough to include them in the analysis
    f=open('axis%d'%tt,'rb')
    flip=pk.load(f)
    f.close()

    if flip<=0.001:


    	f=open('run_p.job', 'w')
    	f.write("#!/bin/bash")
    	f.write("\n")
    	f.write("#PBS -N P%d"%tt)
    	f.write("\n")
    	f.write("#PBS -W group_list=oiz")
    	f.write("\n")
    	f.write("#PBS -q standard")
    	f.write("\n")
    	f.write("#PBS -l select=1:ncpus=1:mem=6gb:pcmem=6gb")
    	f.write("\n")
    	f.write("#PBS -l place=free:shared")
    	f.write("\n")
    	f.write("#PBS -l walltime=00:10:00")
    	f.write("\n")
    	f.write("#PBS -l cput=00:10:00")
    	f.write("\n")
    	f.write("cd /home/u23/tejakondury/EXPAN")
    	f.write("\n")
    	f.write("abaqus cae noGUI=no_pore_cte.py ")
    	f.close()

    	os.environ['tt']=str(tt)
        os.environ['pr_vol']=str(pore_vol)
        os.environ['mat_vol']=str(mat_vol)

    	subprocess.call('qsub -v tt=$tt,mat_vol=$mat_vol,pr_vol=$pr_vol run_p.job',shell=True)

        print('analysis is submitted for temp',tt)
        time.sleep(45)

    else:


    	f=open('run_p.job', 'w')
    	f.write("#!/bin/bash")
    	f.write("\n")
    	f.write("#PBS -N P%d"%tt)
    	f.write("\n")
    	f.write("#PBS -W group_list=oiz")
    	f.write("\n")
    	f.write("#PBS -q standard")
    	f.write("\n")
    	f.write("#PBS -l select=1:ncpus=1:mem=6gb:pcmem=6gb")
    	f.write("\n")
    	f.write("#PBS -l place=free:shared")
    	f.write("\n")
    	f.write("#PBS -l walltime=00:10:00")
    	f.write("\n")
    	f.write("#PBS -l cput=00:10:00")
    	f.write("\n")
    	f.write("cd /home/u23/tejakondury/EXPAN")
    	f.write("\n")
     	f.write("abaqus cae noGUI=pore_cte_hbc.py")
	f.close()



        os.environ['tt']= str(tt)
    	os.environ['pr_vol']=str(pore_vol)
    	os.environ['mat_vol']=str(mat_vol)
        #os.environ['p_tot']=str(p_tot)


	subprocess.call('qsub -v tt=$tt,mat_vol=$mat_vol,pr_vol=$pr_vol,p_tot=$p_tot run_p.job',shell=True)
        time.sleep(45)

        print('analysis is submitted for temp',tt)
