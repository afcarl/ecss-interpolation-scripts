# -*- coding: mbcs -*-
# Do not delete the following import lines
import visualization
from abaqus import *
from abaqusConstants import *
import displayGroupOdbToolset as dgo
import os

filename = os.environ["ODB_FILENAME"]
folder = "outputs_S_july17_" + filename.replace(".odb","")
try:
    os.mkdir(folder)
except:
    pass

from odbAccess import openOdb
o1 = openOdb(filename)

model = "5um" if "5um" in filename else "6um"
from ext_set2 import s

for tag in s.keys():
    regions = set([tup[0] for tup in s[tag][model]])
    for region in regions:
        region_nodes = [tup for tup in s[tag][model] if tup[0] == region]
        num_region_nodes = len(region_nodes)
        session.viewports['Viewport: 1'].setValues(displayedObject=o1)
        leaf = dgo.LeafFromModelNodeLabels(nodeLabels=region_nodes)
        dg = session.DisplayGroup(leaf=leaf, name=tag)
        session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)

        out_filename = os.path.join(folder, filename.replace(".odb", '_{}_set'.format(tag)))
        session.writeFieldReport(fileName="_".join([out_filename,region,'{}.rpt'.format(num_region_nodes)]), append=OFF, 
            sortItem='Node Label', odb=o1, step=0, frame=1, outputPosition=NODAL, 
            variable=(('S', INTEGRATION_POINT), ))
