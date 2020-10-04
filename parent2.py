import os
import subprocess
import numpy as np
import time
import props as p
import pickle as pk
from scipy.interpolate import interp1d

data1 =np.loadtxt('results_cte')
data2=np.loadtxt('results_emod') # elastic modulus results
data3=np.loadtxt('results_cond') # conductivity results
#data1=np.loadtxt('stat_mat_output')   # use this while considering averaged first step results

len=len(data1)
tt=np.zeros(len)
cte_matrix=np.zeros(len)


for i in xrange(len):
    tt[i]=data1[i][0]
    cte_matrix[i]=data1[i][1]


for i in xrange(len):
    tk=tt[i]
    # matrix cte
    cte_mat=cte_matrix[i]
    f=open('cte-mat%d'%tk,'wb')
    pk.dump(cte_mat,f,protocol=2)
    f.close()
    # fiber cte
    cte_fib=(8.026-0.0008*tk-6e-7*tk**2-7e-21*tk**3)*10**-6
    f=open('cte-fib%d'%tk,'wb')
    pk.dump(cte_fib,f,protocol=2)
    f.close()

    # get other homogenized matrix values from previous simulations
    for j in xrange(len(data2)):
        if tk=data2[j][0]:    # For exact match
            mod_mat=data2[j][1]
            pois_mat=data2[j][2]

        elif tk!=data2[j][0]:
            print 'Exact temperature match not found for',tk
            print 'Using linear interpolation for elastic modulus'
            int_mod=interp1d(data2[:][0],data2[:][1])
            int_pois=interp1d(data2[:][0],data2[:][1])
            mod_mat=int_mod(tk)
            pois_mat=int_pois(tk)

    f=open('mod-mat%d'%tk,'wb')
    pk.dump(mod_mat,f,protocol=2)
    f.close()
    f=open('pois-mat%d'%tk,'wb')
    pk.dump(pois_mat,f,protocol=2)
    f.close()

    # for thermal conductivity of homogenized matrix
    for j in xrange(len(data3)):
        if tk=data3[j][0]:
            cond_mat=data3[j][1]

        elif tk!=data3[j][0]:
            print 'Exact temperature match not found for',tk
            print 'Using linear interpolation for conductivity'
            int_cond=interp1d(data3[:][0],data3[:][1])
            cond_mat=int_cond(tk)

    f=open('cond-mat%d'%tk,'wb')
    pk.dump(cond_mat,f,protocol=2)
    f.close()


    f=open('mod-fib%d'%tk,'w')
    pk.dump(p.mod_fib,f,protocol=2)
    #f.write(str(p.mod_fib))
    f.close()
    f=open('pois-fib%d'%tk,'wb')
    pk.dump(p.pois_fib,f,protocol=2)
    #f.write(str(p.pois_fib))
    f.close()
    f=open('cond-fib%d'%tk,'wb')
    pk.dump(p.cond_fib,f,protocol=2)
    f.close()


    f=open('run_p.job', 'w')
    f.write("#!/bin/bash")
    f.write("\n")
    f.write("#PBS -N P%d"%tk)
    f.write("\n")
    f.write("#PBS -W group_list=oiz")
    f.write("\n")
    f.write("#PBS -q standard")
    f.write("\n")
    f.write("#PBS -l select=1:ncpus=8:mem=48gb:pcmem=6gb")
    f.write("\n")
    f.write("#PBS -l place=free:shared")
    f.write("\n")
    f.write("#PBS -l walltime=00:10:00")
    f.write("\n")
    f.write("#PBS -l cput=00:10:00")
    f.write("\n")
    f.write("cd /home/u23/tejakondury/EXPAN")
    f.write("\n")
    f.write("abaqus cae noGUI=comp_cte_2d_fibs_hbc.py ")  # choose a different file for long props
    f.close()

    os.environ['tt']=str(tk)

    subprocess.call('qsub -v tt=$tt run_p.job',shell=True)

    print('analysis is submitted for temp',tk)

    time.sleep(45)
