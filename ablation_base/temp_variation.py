# Defining material properties variation with temperature
from __main__ import *
def temp_variation(tt):

    import numpy as np

    

    if tt>450:
   	cond_mat_var=cond_mat
    else:
	cond_mat_var=cond_mat	
   	#cond_mat_var=0.0962+0.0002342*tt      # data from Farmer and Covert 1994
	
    #cond_mat_var=0.382+(4.263e-3*tt)-(4.057e-5*tt**2)+(1.111e-7*tt**3)-(9.522e-11*tt**4)

    #cond_mat_var=0.382+(4.263e-3*tt)-4.057*e-5*(tt**2)+1.11e-7*(tt**3)-9.522e-11*(tt**4)
    #cond_mat_var=np.sqrt((tt/theta_0))*cond_mat
    #cond_fib_var=np.sqrt((tt/theta_0))*cond_fib
    cond_fib_var=cond_fib
    #cond_pore_var=np.sqrt((tt/theta_0))*cond_pore
    cond_pore_var=cond_pore	

    # dump the values in a binary
    import pickle as pk

    #f=open('cond-mat%d' %tt ,'w')
    #f.write(str(cond_mat_var))
    #f.close()

    f= open('cond-mat%d' %tt,'wb')
    pk.dump(cond_mat_var,f,protocol=2)
    f.close()

    f= open('cond-fib%d' %tt,'wb')
    pk.dump(cond_fib_var,f,protocol=2)
    f.close()

    f= open('cond-pore%d' %tt,'wb')
    pk.dump(cond_pore_var,f,protocol=2)
    f.close()
