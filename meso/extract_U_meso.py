import visualization
from abaqus import *
from abaqusConstants import *
import os
filename = os.environ["MESO_FILENAME"]
from odbAccess import openOdb
o1 = openOdb(filename)
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
odb = session.odbs[filename]
session.writeFieldReport(fileName=filename.replace(".odb", "_U.rpt"), append=ON, 
    sortItem='Node Label', odb=odb, step=0, frame=1, outputPosition=NODAL, 
    variable=(('U', NODAL), ))
session.writeFieldReport(fileName=filename.replace(".odb", "_S.rpt"), append=ON, 
    sortItem='Node Label', odb=odb, step=0, frame=1, outputPosition=NODAL, 
    variable=(('S', INTEGRATION_POINT), ))
