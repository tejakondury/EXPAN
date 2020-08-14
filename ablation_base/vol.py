# calculating the volume fracions at any given temperature

from __main__ import *
def vol(tt):

    temp=symbols('temp')
    tau=symbols('tau')

    a=0.0
    b=(temp-theta_0)/thetadot

    theta=theta_0+(thetadot*tau)
    expr=exp(-ear/theta)
    dumm=integrate(expr,(tau,a,b))
    gg=(-j_0/rho2)*dumm


    psi2=psi2_0*exp(gg)      #matrix decay
    psi3=(psi2_0-psi2)*(1-gamm)*(rho2/rho3)
    psi4=1-(psi1+psi2+psi3)   # pore increase

    # substitute temp at which you require values

    mat_vol=abs(psi2.subs(temp,tt)).evalf()
    pore_vol=abs(psi4.subs(temp,tt)).evalf()

    print ('The pore volume fraction at this temperature should be: ',pore_vol)

    return mat_vol, pore_vol
