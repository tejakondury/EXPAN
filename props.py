# Define room temperature properties of all phases here

#Kinetic parameters
ear=7.8e3
gamm=0.7
j_0=3.6e5

# Heating rates
thetadot=0.1
theta_0=293.0

# initial volume fraction of composite

psi1= 0.0          # vol frac of fibers initial
psi2_0=  1         # matrix
#psi3=   0.0        #char
#psi4=   0.0        #pores

# Densities

rho1=1790.0
rho2=1265.0
rho3=2000.0
rho4=1.0

# Elastic properties

mod_mat= 4.24  #Gpa (Banea et al 2012) # value reset in temperaturue variation.py
pois_mat= 0.38
#mod_fib=19   # Gpa Sun 1996, Cairns et al  # transverse properties
mod_fib=231 # Gpa long props # manufacturer value
pois_fib=0.2 # Sun 1996, Cairns et al
mod_pore=0.00000001
pois_pore=0.1

# Conductivity
# values will be set in temp_variation.py
# Using static analysis so conductivity values are not required
cond_mat= 1
cond_pore= 1
cond_fib= 1

# Expansion
# values will be set in temperature_variation.py
cte_mat= 1
cte_pore= 1
cte_fib= 1
