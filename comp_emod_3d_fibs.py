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

# get initial data
from __main__ import *
# read conductivity values from previous step
f=open('emod_mat%d'%tt,'r')
mod_mat_var=f.read()
mod_mat_var=float(mod_mat_var)
f.close()

f=open('pois_mat%d'%tt,'r')
pois_mat_var=f.read()
pois_mat_var=float(pois_mat_var)
f.close()

# check fiber properties!!!!
f=open('mod-fib%d'%tt,'r')
mod_fib_var=f.read()
mod_fib_var=float(mod_fib_var)
f.close()

f=open('pois-fib%d' %tt,'r')
pois_fib_var=f.read()
pois_fib_var=float(pois_fib_var)
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

mdb.models['Model-1'].Material(name='Matrix')
mdb.models['Model-1'].materials['Matrix'].Elastic(table=((mod_mat_var, pois_mat_var), ))
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
# Create dummy nodes (3)

# Dummy node for left-right face
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(-W/2.0,H/2.0,D/2.0))
mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
toName='dummy L-R')

# Create a set of dummy node
r1 = a.referencePoints
keys = r1.keys()
val1 = keys[0]
dummy=(r1[val1], )
a.Set(referencePoints=dummy, name='dummy L-R')

# Dummy node for Top-Bottom face
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(W/2.0,-H/2.0, D/2.0))
mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
toName='dummy T-B')
# Create a set
r1 = a.referencePoints
keys = r1.keys()
val2 = keys[0]
dummy=(r1[val2], )
a.Set(referencePoints=dummy, name='dummy T-B')


# Dummy node for front-back face
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(W/2.0,H/2.0,-D/2.0))
mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1',
toName='dummy F-B')

# Create a set of dummy node
r1 = a.referencePoints
keys = r1.keys()
val3 = keys[0]
dummy=(r1[val3], )
a.Set(referencePoints=dummy, name='dummy F-B')

#mdb.saveAs('/home/u23/tejakondury/RUBY1/mod%d' %tt)


###############################################################################
# Applying constraint equations
#Apply constraint equation to each corresponding node for Periodic Boundary Condition (left to right faces, x faces)
for j in range(1,nodeno1):

    mdb.models['Model-1'].Equation(name='LeftRight-xdisp-Constraint-%d'%(j), terms=((1.0, 'LeftNode-%d'%(j), 1), (-1.0, 'RightNode-%d'%(j), 1),(-1.0, 'dummy L-R', 1)))
    mdb.models['Model-1'].Equation(name='LeftRight-ydisp-Constraint-%d'%(j), terms=((1.0, 'LeftNode-%d'%(j), 2), (-1.0, 'RightNode-%d'%(j), 2),(-1.0, 'dummy L-R', 2)))
    mdb.models['Model-1'].Equation(name='LeftRight-zdisp-Constraint-%d'%(j), terms=((1.0, 'LeftNode-%d'%(j), 3), (-1.0, 'RightNode-%d'%(j), 3),(-1.0, 'dummy L-R', 3)))
#Apply constraint equation to each corresponding node for Periodic Boundary Condition (top to bottom faces, y faces)
for j in range(1,nodeno3):

    mdb.models['Model-1'].Equation(name='TopBottom-xdisp-Constraint-%d'%(j), terms=((1.0, 'TopNode-%d'%(j), 1), (-1.0, 'BottomNode-%d'%(j), 1),(-1.0, 'dummy T-B', 1)))
    mdb.models['Model-1'].Equation(name='TopBottom-ydisp-Constraint-%d'%(j), terms=((1.0, 'TopNode-%d'%(j), 2), (-1.0, 'BottomNode-%d'%(j), 2),(-1.0, 'dummy T-B', 2)))
    mdb.models['Model-1'].Equation(name='TopBottom-zdisp-Constraint-%d'%(j), terms=((1.0, 'TopNode-%d'%(j), 3), (-1.0, 'BottomNode-%d'%(j), 3),(-1.0, 'dummy T-B', 3)))

#Apply constraint equation to each corresponding node for Periodic Boundary Condition (front to back faces, z faces)
for j in range(1,nodeno5):

    mdb.models['Model-1'].Equation(name='FrontBack-xdisp-Constraint-%d'%(j), terms=((1.0, 'FrontNode-%d'%(j), 1), (-1.0, 'BackNode-%d'%(j), 1),(-1.0, 'dummy F-B', 1)))
    mdb.models['Model-1'].Equation(name='FrontBack-ydisp-Constraint-%d'%(j), terms=((1.0, 'FrontNode-%d'%(j), 2), (-1.0, 'BackNode-%d'%(j), 2),(-1.0, 'dummy F-B', 2)))
    mdb.models['Model-1'].Equation(name='FrontBack-zdisp-Constraint-%d'%(j), terms=((1.0, 'FrontNode-%d'%(j), 3), (-1.0, 'BackNode-%d'%(j), 3),(-1.0, 'dummy F-B', 3)))

###################################################################################
# Create step
a = mdb.models['Model-1'].rootAssembly
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
#####################################################################################
# Apply boundary conditions on dummy nodes
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=dummy=(r1[val3], )
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
    region=region,u1=0.0,u2=0.0,u3=0.1, amplitude=UNSET, fixed=OFF,
    distributionType=UNIFORM, fieldName='' )

#### change BCs!!!!!
# left-right
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=dummy=(r1[val1], )
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
     region=region,u2=0.0,u3=0.0, amplitude=UNSET, fixed=OFF,
     distributionType=UNIFORM, fieldName='' )

# top-bottom
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=dummy=(r1[val2], )
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
     region=region,u1=0.0,u3=0.0, amplitude=UNSET, fixed=OFF,
     distributionType=UNIFORM, fieldName='' )


#######################################################################################

# Create a job
mdb.Job(name='Job%d'%tt, model='Model-1', description='', type=ANALYSIS,
atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
#mdb.jobs['Job-1'].setValues(multiprocessingMode=MPI,numCpus=3, numDomains=3)
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2',
createStepName='Step-1', variables=('IVOL', ))

mdb.saveAs('/home/u23/tejakondury/ONYX/mod3_%d' %tt)
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

E_eff=totStress/totStrain # This is calculating sigma11/E11

# Calculate the poissons ratio as well
transStrain=0.0
totVol=0.0
comp=1 # This will reference E22ls

for j in xrange(0,len(vol.values)):
	setVol = vol.values[j].data
	totVol += setVol
	transStrain += strain.values[j].data[comp]*setVol

# Poisson ratio
pois_eff=-transStrain/totStrain

f=open('results_emod_long_composite','a')
f.write(str(tt)+' '+str(E_eff)+' '+str(pois_eff)+"\n")
f.close()
