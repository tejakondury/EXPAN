import os
tts=os.environ['tt']
tt=float(tts)
# Abaqus modules
from abaqus import *
from abaqusConstants import *
from caeModules import *

# Python modules
import os
import numpy as np
import pickle as pk

# Get initial data from the 1st step

# Lumped phase properties
f=open('mod-mat%d'%tt,'rb')
mod_mat_var=pk.load(f)
f.close()
f=open('pois-mat%d'%tt,'rb')
pois_mat_var=pk.load(f)
f.close()
f=open('cte-mat%d' %tt, 'rb')
cte_mat_var=pk.load(f)
f.close()
f=open('cond-mat%d'%tt,'rb')
cond_mat_var=pk.load(f)
f.close()


## Fiber properties
f=open('mod-fib%d'%tt,'rb')
mod_fib_var=pk.load(f)
f.close()
f=open('pois-fib%d'%tt,'rb')
pois_fib_var=pk.load(f)
f.close()
f=open('cte-fib%d'%tt,'rb')
cte_fib_var=pk.load(f)
f.close()
f=open('cond-fib%d'%tt,'rb')
cond_fib_var=pk.load(f)
f.close()

Mdb

##############################################################
# Read from packing data
# import data1 and create arrays
data1 = np.loadtxt('ellipse_positions2' + '.txt',skiprows=2)
print data1
ctr = np.zeros(shape=(len(data1),3))
pt1 = np.zeros(shape=(len(data1),3))
pt2 = np.zeros(shape=(len(data1),3))
for i in xrange(len(data1)):
	ctr[i]=data1[i][0:3]
	pt1[i]=data1[i][3:6]
	pt2[i]=data1[i][6:9]


data2 = np.loadtxt('packing_info2' + '.txt',skiprows=0)
print data2
N_fiber = int(data2[0])
N_pore = int(data2[2])
N=N_fiber+N_pore

########################################################################3
# Create material properties
mdb.models['Model-1'].Material(name='Fiber')
mdb.models['Model-1'].materials['Fiber'].Elastic(table=((mod_fib_var, pois_fib_var), ))
mdb.models['Model-1'].materials['Fiber'].Conductivity(table=((cond_fib_var,), ))
mdb.models['Model-1'].materials['Fiber'].Expansion(table=((cte_fib_var,), ))

mdb.models['Model-1'].Material(name='Matrix')
mdb.models['Model-1'].materials['Matrix'].Elastic(table=((mod_mat_var, pois_mat_var), ))
mdb.models['Model-1'].materials['Matrix'].Conductivity(table=((cond_mat_var,), ))
mdb.models['Model-1'].materials['Matrix'].Expansion(table=((cte_mat_var,), ))
##############################################################################
# rectangle
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
H=1.0
W=1.0
s.rectangle(point1=(0.0, 0.0), point2=(W, H))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)

###############################################################################

for i in xrange(N_fiber):
    p = mdb.models['Model-1'].parts['Part-1']
    f1, e1, d2 = p.faces, p.edges, p.datums
    t = p.MakeSketchTransform(sketchPlane=f1.findAt(coordinates=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0)), sketchUpEdge=e1.findAt(
    coordinates=(W, H/2.0, 0.0)), sketchPlaneSide=SIDE1, origin=(0.0, 0.0,
    0.0))
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=2.82, gridSpacing=0.07, transform=t)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=SUPERIMPOSE)
    p = mdb.models['Model-1'].parts['Part-1']
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.EllipseByCenterPerimeter(center=(ctr[i][0], ctr[i][1]), axisPoint1=(pt1[i][0],pt1[i][1]), axisPoint2=(pt2[i][0],pt2[i][1]))
    p = mdb.models['Model-1'].parts['Part-1']
    f = p.faces
    pickedFaces = f.findAt(((0.0, 0.0, 0.0), ))
    e, d1 = p.edges, p.datums
    p.PartitionFaceBySketch(faces=pickedFaces, sketch=s)


######################################################################

# Create sections

mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
     material='Matrix', thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-2',
     material='Fiber', thickness=None)

######################################################################

# Create sets
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.findAt(((0.0, 0.0, 0.0), ))
p.Set(faces=faces, name='Matrix')


# Create a set of the fibers
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.findAt(((ctr[0][0],ctr[0][1],0.0), ) )
for i in xrange(1,N_fiber):
	faces += f.findAt(((ctr[i][0],ctr[i][1],0.0), ) )
p.Set(faces=faces, name='Fiber')




####################################################################
# Assign sections
p = mdb.models['Model-1'].parts['Part-1']
region = p.sets['Matrix']
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
    offsetType=MIDDLE_SURFACE, offsetField='',
    thicknessAssignment=FROM_SECTION)

p = mdb.models['Model-1'].parts['Part-1']
region = p.sets['Fiber']
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-2', offset=0.0,
    offsetType=MIDDLE_SURFACE, offsetField='',
    thicknessAssignment=FROM_SECTION)

#################################################################################


# Create instance
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=OFF)

#############################################################################

# Change form here##########################
########################################
##################################

# Assign element types
elemType1=mesh.ElemType(elemCode=CPS4R,elemLibrary=STANDARD)
p=mdb.models['Model-1'].parts['Part-1']
a = mdb.models['Model-1'].rootAssembly
f1 =a.instances['Part-1-1'].faces
#faces1=f1.findAt(((0.0,0.0,0.0),),((0.2,0.2,0.0),),((0.8,0.2,0.0),),((0.2,0.7,0.0),))
faces1 = f1.getByBoundingBox(0.0,0.0,0.0, 1.0, 1.0, 0.0) # (xmin, ymin, zmin, xmax, ymax, zmax) make this so these will adjust with the RVE size
pickedRegions=(faces1,)
a.setElementType(regions=pickedRegions,elemTypes=(elemType1,))

##################################################################################

# Generate mesh
a = mdb.models['Model-1'].rootAssembly
partInstances =(a.instances['Part-1-1'], )
a.seedPartInstance(regions=partInstances, size=0.05,deviationFactor=0.08,
    minSizeFactor=0.1)
a.generateMesh(regions=partInstances)

###################################################################################
# Create edge sets
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
edges1 = e1.findAt(((0.0, H/2, 0.0), ))

a.Set(edges=edges1, name='left')

a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
edges1 = e1.findAt(((W, H/2, 0.0), ))
a.Set(edges=edges1, name='right')

# top set
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges

edges1=e1.findAt(((W/2,H,0.0),))
xv1 = a.instances['Part-1-1'].vertices

xVerts1=xv1.findAt(((0.0,H,0.0),),((W,H,0.0),))
a.Set(edges=edges1, xVertices=xVerts1, name='top')

# bottom set

a = mdb.models['Model-1'].rootAssembly
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges

edges1=e1.findAt(((W/2,0.0,0.0),))
xv1 = a.instances['Part-1-1'].vertices
xVerts1=xv1.findAt(((0.0,0.0,0.0),),((W,0.0,0.0),))
a.Set(edges=edges1, xVertices=xVerts1, name='bottom')

#Create individual nodes from the set
    # left side
n1 = []
for i in a.sets['left'].nodes:
    n1.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n1.sort()

#Create a set from individual nodes in set above
nodeno1 = 1
for i in n1:
    setName = 'LeftNode-' + str(nodeno1)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno1 += 1

    # right side
n2 = []
for i in a.sets['right'].nodes:
    n2.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n2.sort()

#Create a set from individual nodes in set above
nodeno2 = 1
for i in n2:
    setName = 'RightNode-' + str(nodeno2)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno2 += 1

    #top
n3 = []
for i in a.sets['top'].nodes:
    n3.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n3.sort()

nodeno3 = 1
for i in n3:
    setName = 'TopNode-' + str(nodeno3)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno3 += 1

    #bottom
n4 = []
for i in a.sets['bottom'].nodes:
    n4.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n4.sort()

nodeno4 = 1
for i in n4:
    setName = 'BottomNode-' + str(nodeno4)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('Part-1-1', (i[3],),),),)
    nodeno4 += 1

###################################################################################
# Create dummy node
# a = mdb.models['Model-1'].rootAssembly
# a.ReferencePoint(point=(-0.5, 1.0, 0.0))
# mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
#     toName='dummy')
#
# #Apply PBC nodal constraint equations
# r1 = a.referencePoints
# keys = r1.keys()
# val1 = keys[0]
# dummy=(r1[val1], )
# a.Set(referencePoints=dummy, name='dummy')
#
# # Create dummy node
# a = mdb.models['Model-1'].rootAssembly
# a.ReferencePoint(point=(0, 1.5, 0.0))
# mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
#     toName='dummy2')
#
# #Apply PBC nodal constraint equations
# r1 = a.referencePoints
# keys = r1.keys()
# val2 = keys[0]
# dummy=(r1[val2], )
# a.Set(referencePoints=dummy, name='dummy2')
#

#########################################################################################

#Apply constraint equation to each corresponding node for Periodic Boundary Condition (left to right faces, x faces)
# for j in range(1,nodeno1):
#
#     mdb.models['Model-1'].Equation(name='LeftRight-xdisp-Constraint-%d'%(j), terms=((1.0, 'LeftNode-%d'%(j), 1), (-1.0, 'RightNode-%d'%(j), 1),(-1.0, 'dummy', 1)))
#     mdb.models['Model-1'].Equation(name='LeftRight-ydisp-Constraint-%d'%(j), terms=((1.0, 'LeftNode-%d'%(j), 2), (-1.0, 'RightNode-%d'%(j), 2),(-1.0, 'dummy', 2)))
#
#
# #Apply constraint equation to each corresponding node for Periodic Boundary Condition (top to bottom faces, y faces)
# for j in range(1,nodeno3):
#
#     mdb.models['Model-1'].Equation(name='TopBottom-disp-Constraint-%d'%(j), terms=((1.0, 'TopNode-%d'%(j), 1), (-1.0, 'BottomNode-%d'%(j), 1),(-1.0, 'dummy2', 1)))
#     mdb.models['Model-1'].Equation(name='TopBottom-disp-Constraint-%d'%(j), terms=((1.0, 'TopNode-%d'%(j), 2), (-1.0, 'BottomNode-%d'%(j), 2),(-1.0, 'dummy2', 2)))
#
#
###################################################################################
# Create step
#a = mdb.models['Model-1'].rootAssembly
#mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
# using a coupled-temperature displaement step
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')

######################################################################################

# Applying HBC
# In the x-direction
# Apply temperature loads as predefined field
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-1']
f=a.instances['Part-1-1'].faces
f1=f.getByBoundingBox(0.0,0.0,0.0,1.0,1.0,0.0)
region=a.Set(faces=f1,name='all')
# set initial temperature as 20 C
mdb.models['Model-1'].Temperature(name='Predefined Field-1',
	createStepName='Initial', region=region, distributionType=UNIFORM,
	crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, magnitudes=(20.0,
	))
# raise to final temperature of 100 C
mdb.models['Model-1'].Temperature(name='Predefined Field-2',
	createStepName='Step-1', region=region, distributionType=UNIFORM,
	crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, magnitudes=(100.0,
	))

# Apply homogenuous Boundary conditions
region = a.sets['left']
mdb.models['Model-1'].XsymmBC(name='BC-1', createStepName='Step-1',
	region=region, localCsys=None)
region=a.sets['bottom']
mdb.models['Model-1'].YsymmBC(name='BC-2', createStepName='Step-1',region=region,localCsys=None)



#######################################################################################

# Create a job
mdb.Job(name='Job%d' %tt, model='Model-1', description='', type=ANALYSIS,
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
    scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
#mdb.jobs['Job%d' %tt].setValues(multiprocessingMode=MPI,numCpus=3, numDomains=3)

mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2',
    createStepName='Step-1', variables=('IVOL', ))
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-3',
	    createStepName='Step-1', variables=('THE', ))
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-4',
	    createStepName='Step-1', variables=('TEMP', ))
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-5',
		    createStepName='Step-1', variables=('EE', ))


mdb.saveAs('/home/u23/tejakondury/ONYX/mod_2%d' %tt)
###########################################################################################

#Submit job
mdb.jobs['Job%d' %tt].submit(consistencyChecking=OFF)
mdb.jobs['Job%d' %tt].waitForCompletion()

#############################################################################################
################
#Post processing
#################
#Import abaqus functions
#Import abaqus functions
from odbAccess import*

#odb job information
OdbName = 'Job%d.odb' %tt
myodb = openOdb(path=OdbName)

numFrames = len(myodb.steps['Step-1'].frames) #total number of frames
vol = myodb.steps['Step-1'].frames[-1].fieldOutputs['IVOL']
stress=myodb.steps['Step-1'].frames[-1].fieldOutputs['S']
strain=myodb.steps['Step-1'].frames[-1].fieldOutputs['E']  # thermal strain component
#temp=myodb.steps['Step-1'].frames[-1].fieldOutputs['TEMP']  # elemental temperature

comp=0    # change here if you are loading in different direction other than x-direction
totVol = 0.0
totStress=0.0
totStrain=0.0
totTemp=0.0

for j in range(0,len(vol.values)):
	setVol = vol.values[j].data
	totVol += setVol
	totStress += stress.values[j].data[comp]*setVol
	totStrain += strain.values[j].data[comp]*setVol

totStress=totStress/totVol
totStrain=totStrain/totVol

cte_eff=totStrain/totTemp # This is calculating sigma11/E11

f=open('results_comp_cte','a')
f.write(str(tt)+' '+str(cte_eff)+ "\n")
f.close()
