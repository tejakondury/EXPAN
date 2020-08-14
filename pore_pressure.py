# Module to calculate the pore pressure in a carbon epoxy laminate undergoing ablation
import numpy as np
data2 = np.loadtxt('packing_info' + '.txt',skiprows=0)
N_fiber = int(data2[0])
N_pore = int(data2[2])

#need as input:: pore volume, number of pores

# Universal gas constant
R=8.314462   #m3.Pa/K.mol

#densities of gaseous species
d_h20= 590.34 #g/m3
d_co2= 1815.1
d_co= 1150.2
d_so2= 2678.4
d_ch4= 659.75
d_nh3= 706.96

# molecular masses of gaseous species
mm_h2o=18.01   #g/mol
mm_co2=44.01
mm_co=28.01
mm_so2=64.06
mm_ch4=16.04
mm_nh3=17.03


# List the species with their volume fraction
# data taken from Tranchard et al
v_h2o=0.675
v_co2=0.213
v_co=0.038
v_so2=0.039
v_ch4=0.019
v_nh3=0.01

# convert volume fraction to mole fractions (identical for an ideal gas)

# calculate number of moles from mole fractions

# only for eaual pores shapes and volumes
# need to change for 3d case
 vol_pore_i=pore_vol/N_pore  # volume of individual pores

# calculate the individual species volumes
vol_h2o=v_h2o*vol_pore_i
vol_co2=v_co2*vol_pore_i
vol_co=v_co*vol_pore_i
vol_so2=v_so2*vol_pore_i
vol_ch4=v_ch4*vol_pore_i
vol_nh3=v_nh3*vol_pore_i

# Convert voulme to mass

m_h2o=vol_h20*d_h20
m_co2=vol_co2*d_co2
m_co=vol_co*d_co
m_so2=vol_so2*d_so2
m_ch4=vol_ch4*d_ch4
m_nh3=vol_nh3*d_nh3

# convert mass to moles

n_h2o=m_h20/mm_h20
n_co2=m_co2/mm_co2
n_so2=m_so2/mm_so2
n_ch4=m_ch4/mm_ch4
n_nh3=m_nh3/mm_nh3

# Estimate pressure exerted by each species

p_h20=n_h20*R*tt/vol_pore_i
p_co2=n_co2*R*tt/vol_pore_i
p_so2=n_so2*R*tt/vol_pore_i
p_ch4=n_ch4*R*tt/vol_pore_i
p_nh3=n_nh3*R*tt/vol_pore_i

# Total pressure
p_tot=p_h2o+p_co2+p_so2+p_ch4+p_nh3

return p_tot
