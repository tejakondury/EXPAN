# Ablation base module containing ablation functions
def pack(pore_vol,tt):

    ##############################################################
    # Read from packing data
    # import data1 and create arrays

    import numpy as np
    import pickle as pk
    #from props import *

    data1 = np.loadtxt('ellipse_positions' + '.txt',skiprows=2)
    #print (data1)
    ctr = np.zeros(shape=(len(data1),3))
    pt1 = np.zeros(shape=(len(data1),3))
    pt2 = np.zeros(shape=(len(data1),3))
    ang = np.zeros(shape=(len(data1),1))

    for i in range(len(data1)):
        ctr[i]=data1[i][0:3]
        pt1[i]=data1[i][3:6]
        pt2[i]=data1[i][6:9]
        ang[i]=data1[i][9]




    data2 = np.loadtxt('packing_info' + '.txt',skiprows=0)
    N_fiber = int(data2[0])
    N_pore = int(data2[2])
    N=N_fiber+N_pore
    print ('N fiber = ', N_fiber)
    print ('N pore = ', N_pore)



    ################################################3
    # Calculate the aspect ratios of any one pore

    k=N_fiber+1
    a=((ctr[k][0]-pt1[k][0])**2+(ctr[k][1]-pt1[k][1])**2)**0.5
    b=((ctr[k][0]-pt2[k][0])**2+(ctr[k][1]-pt2[k][1])**2)**0.5

    R=a/b

    print 'The aspect ratio is =',R
    ######################################
    # calculate the present volume fraction
    pr_vol_frac_pore=N_pore*(np.pi*a*b)

    print ('pore vol frac', pr_vol_frac_pore)

    ####################################3

    # desired vol fraction is pore_vol

    print ('New volume of the pores is',pore_vol)

    a_new_mod=(pore_vol*R/(N_pore*np.pi))**0.5    # change here for switching test 1.0
    b_new_mod=a_new_mod/R

    print ('a is' ,a_new_mod )
    print ('b is' ,b_new_mod )

    f=open('asp_ch','a')
    f.write(str(tt)+' '+str(a_new_mod)+"\n")
    f.close()

    f=open('axis%d'%tt,'wb')
    pk.dump(a_new_mod,f,protocol=2)
    f.close()

    ######################################
    # calculate the angles of each ellipse
    ang_calc=[]

    for i in range(N_fiber,N):
        ang_calc.append(np.arctan((pt1[k][2]-ctr[k][2])/pt1[k][1]-ctr[k][1]))


    ## Create new pore positions
    fin_a_x=[]
    fin_a_y=[]
    fin_b_x=[]
    fin_b_y=[]


    for k in range(N_fiber,N):
        fin_a_x.append(a_new_mod*np.cos(ang[k])+ctr[k][0])
        fin_a_y.append(a_new_mod*np.sin(ang[k])+ctr[k][1])
        fin_b_x.append(-b_new_mod*np.sin(ang[k])+ctr[k][0])
        fin_b_y.append(b_new_mod*np.cos(ang[k])+ctr[k][1])


    #print(fin_a_y)
    #print(fin_b_y)

    yay=np.zeros((N_pore,4))

    for i in range(N_pore):
        yay[i][0]=fin_a_x[i]

    for i in range(N_pore):
        yay[i][1]=fin_a_y[i]

    for i in range(N_pore):
        yay[i][2]=fin_b_x[i]

    for i in range(N_pore):
        yay[i][3]=fin_b_y[i]


    np.savetxt('yy%d'%tt,yay)   #where is it used? everywhere.

# Defining material properties variation with temperature
def temp_variation(tt):
    import numpy as np
    import pickle as pk
    import props as p


    # Mechanical_properties
    mod_fib_var=p.mod_fib
    pois_fib_var=p.pois_fib
    mod_pore_var=p.mod_pore
    pois_pore_var=p.pois_pore

    mod_mat_var=float(emod_interp(tt))
    pois_mat_var=float(pois_m(tt))

    # Expansion properties
    # matrix property taken from Cairns and Adams
    if tt<=448:
        cte_mat_var=(4.9277+0.1224*tt)*10**-6
    else:
        cte_mat_var=59.76e-6
    # Fiber property taken from Pradere et al
    #cte_fib_var= (8.026-0.0008*tt-6e-7*tt**2-7e-21*tt**3)*10**-6  # values for PANEX33 at 300K (transverse)
    cte_fib_var=(-2.742+0.0082*tt-5e-6*tt**2+1e-9*tt**3)*10**-6  # values for PANEX33 at 300K (long)
    # transverse properties shows very weak dependnece with temperature
    # property valid for the entire range
    cte_pore_var= 0.0034 # taken from some random reference online, need to check for accuracy.
    # Thermal properties
    # thermal properties are not changed because we are running a static analysis and conductivity values are not required
    cond_mat_var=p.cond_mat
    cond_pore_var=p.cond_pore
    cond_fib_var=p.cond_fib


    # dump the values in a binary
    f= open('mod-mat%d' %tt,'wb')
    pk.dump(mod_mat_var,f,protocol=2)
    f.close()

    f= open('mod-fib%d' %tt,'wb')
    pk.dump(mod_fib_var,f,protocol=2)
    f.close()

    f= open('mod-pore%d' %tt,'wb')
    pk.dump(mod_pore_var,f,protocol=2)
    f.close()

    f=open('pois-mat%d' %tt,'wb')
    pk.dump(pois_mat_var,f,protocol=2)

    f=open('pois-fib%d' %tt,'wb')
    pk.dump(pois_fib_var,f,protocol=2)

    f=open('pois-pore%d' %tt,'wb')
    pk.dump(pois_pore_var,f,protocol=2)

    f=open('cte-mat%d' %tt, 'wb')
    pk.dump(cte_mat_var,f,protocol=2)

    f=open('cte-fib%d' %tt, 'wb')
    pk.dump(cte_fib_var,f,protocol=2)

    f=open('cte-pore%d' %tt, 'wb')
    pk.dump(cte_pore_var,f,protocol=2)

    f=open('cond-mat%d' %tt, 'wb')
    pk.dump(cond_mat_var,f,protocol=2)

    f=open('cond-fib%d' %tt, 'wb')
    pk.dump(cond_fib_var,f,protocol=2)

    f=open('cond-pore%d' %tt, 'wb')
    pk.dump(cond_pore_var,f,protocol=2)


def vol(tt):
# returns volume fractions of each phase
    from sympy import *
    import props as p

    temp=symbols('temp')
    tau=symbols('tau')

    a=0.0
    b=(temp-p.theta_0)/p.thetadot

    theta=p.theta_0+(p.thetadot*tau)
    expr=exp(-p.ear/theta)
    dumm=integrate(expr,(tau,a,b))
    gg=(-p.j_0/p.rho2)*dumm


    psi2=p.psi2_0*exp(gg)      #matrix decay
    psi3=(p.psi2_0-psi2)*(1-p.gamm)*(p.rho2/p.rho3)
    psi4=1-(p.psi1+psi2+psi3)   # pore increase

    # substitute temp at which you require values

    mat_vol=abs(psi2.subs(temp,tt)).evalf()
    pore_vol=abs(psi4.subs(temp,tt)).evalf()

    print ('The pore volume fraction at this temperature should be: ',pore_vol)

    return mat_vol, pore_vol

def pore_pressure(tt):
    # Module to calculate the pore pressure in a carbon epoxy laminate undergoing ablation
    import numpy as np
    data2 = np.loadtxt('packing_info' + '.txt',skiprows=0)
    N_fiber = int(data2[0])
    N_pore = int(data2[2])

    #need as input:: number of pores, temperature

    # Universal gas constant
    R=8.314462   #m3.Pa/K.mol

    # Concentrations of gases in mol/m3   # Concentrations from Tranchard 2015
    alp1=29.16  # H2O
    alp2=25.81 # CO2
    alp3=0.35 #SO2
    alp4=0.17 # NO

    alp_tot=alp1+alp2+alp3+alp4
    # sensitivity study
    # Total press
    #p_tot=(alp1+alp2+alp3+alp4)*R*tt*1e-6
    p_tot=(alp_tot)*R*tt*1e-6
    #p_tot=7.0   # Results from Florio pressure is 7atm=7e6Pa
    # pressure in each pore is distributed equally
    #p_tot=p_tot/N_pore

    return p_tot

def emod_interp(x):
    from scipy.interpolate import interp1d
    import numpy as np
    # function for interpolating the elastic modulus from Augl 1979
    # linear interpolation is used
    t_exp=np.array([25,50,100,150,200]) # in celcius
    # convert temp in kelvin
    t_k=t_exp+273.0
    e_mod=np.array([4.24,4.03,3.66,2.87,0.15]) # In Gpa
    f=interp1d(t_k,e_mod)
    if (x<=473):
        ex=f(x)
    else:
        ex=0.15
    return ex

def pois_m(x):
    # variation in poisson ratio gathered and estimated from different sources.
    if (x<453):
        nux=0.38
    elif (x>=453 and x<483):
        nux=0.38+(3*((x-453)/30)^2-2*((x-453)/30)^3)*0.12
    elif (x>=483):
        nux=0.5
    return nux
