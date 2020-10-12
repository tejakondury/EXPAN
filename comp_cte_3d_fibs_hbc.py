import os
print('this is the env variable:', os.environ['tt'])
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
mod_mat_var=float(pk.load(f))
f.close()
f=open('pois-mat%d'%tt,'rb')
pois_mat_var=float(pk.load(f))
f.close()
f=open('cte-mat%d' %tt, 'rb')
cte_mat_var=float(pk.load(f))
f.close()
f=open('cond-mat%d'%tt,'rb')
cond_mat_var=float(pk.load(f))
f.close()


## Fiber properties
f=open('mod-fib%d'%tt,'rb')
mod_fib_var=float(pk.load(f))
f.close()
f=open('pois-fib%d'%tt,'rb')
pois_fib_var=float(pk.load(f))
f.close()
f=open('cte-fib%d'%tt,'rb')
cte_fib_var=float(pk.load(f))
f.close()
f=open('cond-fib%d'%tt,'rb')
cond_fib_var=float(pk.load(f))
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

######################################################################
# Make a cube
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
# RVE Geometry
H=1.0
W=1.0
D=1.0
s.rectangle(point1=(0.0, 0.0), point2=(W, H))
p = mdb.models['Model-1'].Part(name='Matrix', dimensionality=THREE_D,
type=DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Matrix'].BaseSolidExtrude(depth=D, sketch= mdb.models['Model-1'].sketches['__profile__'])

# make a fiber
rad_fib=np.sqrt((ctr[0][0]-pt1[0][0])**2+(ctr[0][1]-pt1[0][1])**2)

s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
sheetSize=200.0)
p = mdb.models['Model-1'].Part(name='Fiber', dimensionality=THREE_D,
type=DEFORMABLE_BODY)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.CircleByCenterPerimeter(center=(0.0,0.0),point1=(rad_fib,0.0))
mdb.models['Model-1'].parts['Fiber'].BaseSolidExtrude(depth=D, sketch= mdb.models['Model-1'].sketches['__profile__'])


###############################################################################
# Creat Instances
p = mdb.models['Model-1'].parts['Matrix']
a1= mdb.models['Model-1'].rootAssembly
a1.Instance(name='Matrix', part=p, dependent=ON)

# Translate instances
for i in xrange(N_fiber):
    # create instance
    a1 = mdb.models['Model-1'].rootAssembly
    p = mdb.models['Model-1'].parts['Fiber']
    a1.Instance(name='fib%d'%i, part=p, dependent=ON)
    #translate it to the right point
    a1.translate(instanceList=('fib%d'%i, ), vector=(ctr[i][0], ctr[i][1], 0.0))

all_inst=[]
for i in xrange(N_fiber):
    all_inst +=(a1.instances['fib%d'%i],)

all_inst +=(a1.instances['Matrix'],)

a1 = mdb.models['Model-1'].rootAssembly
a1.InstanceFromBooleanMerge(name='composite', instances=(all_inst),keepIntersections=ON,
        originalInstances=SUPPRESS, domain=GEOMETRY)

# Sections
# Create a fiber set for section assignment
p = mdb.models['Model-1'].parts['composite']
c = p.cells
cells = c.findAt(((ctr[0][0],ctr[0][1],0.0), ) )
for i in xrange(1,N_fiber):
    cells += c.findAt(((ctr[i][0],ctr[i][1],0.0), ) )

p.Set(cells=cells, name='Fiber')

# matrix set
p = mdb.models['Model-1'].parts['composite']
f = p.cells
faces = f.findAt(((0.0, 0.0, 0.0), ))
p.Set(cells=faces, name='Matrix')


mdb.models['Model-1'].HomogeneousSolidSection(name='mat-sec',
material='Matrix', thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='fib-sec',
material='Fiber', thickness=None)


# Assign sections
p = mdb.models['Model-1'].parts['composite']
region = p.sets['Matrix']
p = mdb.models['Model-1'].parts['composite']
p.SectionAssignment(region=region, sectionName='mat-sec', offset=0.0,
offsetType=MIDDLE_SURFACE, offsetField='',
thicknessAssignment=FROM_SECTION)


p = mdb.models['Model-1'].parts['composite']
region = p.sets['Fiber']
p = mdb.models['Model-1'].parts['composite']
p.SectionAssignment(region=region, sectionName='fib-sec', offset=0.0,
offsetType=MIDDLE_SURFACE, offsetField='',
thicknessAssignment=FROM_SECTION)


a = mdb.models['Model-1'].rootAssembly
a.makeIndependent(instances=(a.instances['composite-1'], ))


# Assign element types
elemType1=mesh.ElemType(elemCode=C3D8R,elemLibrary=STANDARD)
#elemType2=mesh.ElemType(elemCode=DC2D3,elemLibrary=STANDARD)
p=mdb.models['Model-1'].parts['composite']
a = mdb.models['Model-1'].rootAssembly
c1 =a.instances['composite-1'].cells
#faces1=f1.findAt(((0.0,0.0,0.0),),((0.2,0.2,0.0),),((0.8,0.2,0.0),),((0.2,0.7,0.0),))
faces1 = c1.getByBoundingBox(0.0,0.0,0.0, 1.0, 1.0, 1.0) # (xmin, ymin, zmin, xmax, ymax, zmax) make this so these will adjust with the RVE size
pickedRegions=(faces1,)
a.setElementType(regions=pickedRegions,elemTypes=(elemType1,))

##################################################################################
# Generate mesh

a = mdb.models['Model-1'].rootAssembly
partInstances =(a.instances['composite-1'], )
a.seedPartInstance(regions=partInstances, size=0.04,deviationFactor=0.08,
  minSizeFactor=0.1)
a = mdb.models['Model-1'].rootAssembly
partInstances =(a.instances['composite-1'], )
c1=a.instances['composite-1'].cells
pickedregion=c1.getByBoundingBox(0.0,0.0,0.0,W,H,D)
a.setMeshControls(regions=pickedregion,elemShape=HEX_DOMINATED,allowMapped=False)
a.generateMesh(regions=partInstances)


##########################################################################



# Create sets for faces

w=1.0
D=1.0
H=1.0

a=mdb.models['Model-1'].rootAssembly
f1=a.instances['composite-1'].faces
e1=a.instances['composite-1'].edges
v1=a.instances['composite-1'].vertices

faces1=f1.findAt(((0.0,H/2.0,D/2.0),))
xe1=e1.findAt(((0.0,H/2.0,0.0),),((0.0,H/2.0,D),))
xv1=v1.findAt(((0.0,H,0.0),),((0.0,H,D),),((0.0,0.0,0.0),),((0.0,0.0,D),))
a.Set(faces=faces1,xEdges=xe1,xVertices=xv1,name='left-face')

faces2=f1.findAt(((W,H/2.0,D/2.0),))
xe1=e1.findAt(((W,H/2.0,0.0),),((W,H/2.0,D),))
xv1=v1.findAt(((W,H,0.0),),((W,H,D),),((W,0.0,0.0),),((W,0.0,D),))
a.Set(faces=faces2,xEdges=xe1,xVertices=xv1,name='right-face')

faces3=f1.findAt(((W/2.0,H,D/2.0),))
xe1=e1.findAt(((0.0,H,D/2.0),),((W/2.0,H,0.0),),((W,H,D/2.0),),((W/2.0,H,D),))
xv1=v1.findAt(((0.0,H,0.0),),((0.0,H,D),),((W,H,0.0),),((W,H,D),))
a.Set(faces=faces3,xEdges=xe1,xVertices=xv1, name='top-face')

faces4=f1.findAt(((W/2.0,0.0,D/2.0),))
xe1=e1.findAt(((0.0,0.0,D/2.0),),((W/2.0,0.0,0.0),),((W,0.0,D/2.0),),((W/2.0,0.0,D),))
xv1=v1.findAt(((0.0,0.0,0.0),),((0.0,0.0,D),),((W,0.0,0.0),),((W,0.0,D),))
a.Set(faces=faces4,xEdges=xe1,xVertices=xv1,name='bottom-face')

faces5=f1.getByBoundingBox(0.0,0.0,0.0,W,H,0.0)
a.Set(faces=faces5,name='back-face')

faces6=f1.getByBoundingBox(0.0,0.0,D,W,H,D)
a.Set(faces=faces6,name='front-face')

################################################################################
#Create individual nodes from the set
# left face
n1 = []
for i in a.sets['left-face'].nodes:
    n1.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n1.sort()
#Create a set from individual nodes in set above
nodeno1 = 1
for i in n1:
    setName = 'LeftNode-' + str(nodeno1)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('composite-1', (i[3],),),),)
    nodeno1 += 1

# right side
n2 = []
for i in a.sets['right-face'].nodes:
    n2.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n2.sort()

#Create a set from individual nodes in set above
nodeno2 = 1
for i in n2:
    setName = 'RightNode-' + str(nodeno2)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('composite-1', (i[3],),),),)
    nodeno2 += 1

#top
n3 = []
for i in a.sets['top-face'].nodes:
    n3.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n3.sort()

nodeno3 = 1
for i in n3:
    setName = 'TopNode-' + str(nodeno3)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('composite-1', (i[3],),),),)
    nodeno3 += 1

#bottom
n4 = []
for i in a.sets['bottom-face'].nodes:
    n4.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n4.sort()

nodeno4 = 1
for i in n4:
    setName = 'BottomNode-' + str(nodeno4)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('composite-1', (i[3],),),),)
    nodeno4 += 1

#front

n5 = []
for i in a.sets['front-face'].nodes:
    n5.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n5.sort()

nodeno5 = 1
for i in n5:
    setName = 'FrontNode-' + str(nodeno5)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('composite-1', (i[3],),),),)
    nodeno5 += 1

#back face
n6 = []
for i in a.sets['back-face'].nodes:
    n6.append((i.coordinates[0],i.coordinates[1],i.coordinates[2],i.label))


n6.sort()

nodeno6 = 1
for i in n6:
    setName = 'BackNode-' + str(nodeno6)
    nodeset = a.SetFromNodeLabels(name = setName,nodeLabels = (('composite-1', (i[3],),),),)
    nodeno6 += 1
##########################################################################


###############################################################################
#
###################################################################################
# Create step
a = mdb.models['Model-1'].rootAssembly
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
#####################################################################################
# Apply boundary conditions on dummy nodes
# Applying HBC
# In the x-direction
# Apply temperature loads as predefined field
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['composite']
f=a.instances['composite-1'].faces
f1=f.getByBoundingBox(0.0,0.0,0.0,1.0,1.0,1.0)
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
region = a.sets['left-face']
mdb.models['Model-1'].XsymmBC(name='BC-1', createStepName='Step-1',
	region=region, localCsys=None)
region=a.sets['bottom-face']
mdb.models['Model-1'].YsymmBC(name='BC-2', createStepName='Step-1',region=region,localCsys=None)


#######################################################################################

# Create a job
mdb.Job(name='Job%d'%tt, model='Model-1', description='', type=ANALYSIS,
atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)

mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2',
createStepName='Step-1', variables=('IVOL', ))
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-3',
	    createStepName='Step-1', variables=('THE', ))
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-4',
	    createStepName='Step-1', variables=('TEMP', ))
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-5',
		    createStepName='Step-1', variables=('EE', ))


mdb.saveAs('/home/u23/tejakondury/EXPAN/mod3_%d' %tt)
###########################################################################################

#Submit job
mdb.jobs['Job%d' %tt].submit(consistencyChecking=OFF)
mdb.jobs['Job%d' %tt].waitForCompletion()

#############################################################################################
################
#Post processing
#################
#Import abaqus functions
from odbAccess import*

#odb job information
OdbName = 'Job%d.odb' %tt
myodb = openOdb(path=OdbName)

numFrames = len(myodb.steps['Step-1'].frames) #total number of frames

vol = myodb.steps['Step-1'].frames[-1].fieldOutputs['IVOL']
stress=myodb.steps['Step-1'].frames[-1].fieldOutputs['S']
strain=myodb.steps['Step-1'].frames[-1].fieldOutputs['E']
comp=2    # change here if you are loading in different direction other than x-direction
totVol = 0.0
totStress=0.0
totStrain=0.0

for j in range(0,len(vol.values)):
	setVol = vol.values[j].data
	totVol += setVol
	totStress += stress.values[j].data[comp]*setVol
	totStrain += strain.values[j].data[comp]*setVol

totStress=totStress/totVol
totStrain=totStrain/totVol

cte_eff=totStrain/80.0

f=open('results_comp_long_cte','a')
f.write(str(tt)+' '+str(cte_eff)+"\n")
f.close()
