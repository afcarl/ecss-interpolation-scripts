from __future__ import division, print_function
import sys

import numpy as np
import csv
import logging
from itertools import chain

## Abaqus CAE imports
import visualization
from abaqus import * 
from abaqusConstants import * 

######## CONFIGURATION OPTIONS
filename = "rgtd5-SI91pss.odb"
nodes_filename = "right_femur_nodes.csv"
# logging.DEBUG for verbose output, logging.INFO intermediate, logging.ERROR for quiet
logging_level = logging.DEBUG
########

logging.basicConfig(filename=filename + ".log",level=logging_level, filemode="w")

def flatten_list_of_lists(l):
    return [item for sublist in l for item in sublist]
    
######## Extract coordinates from the odb file and store it in nodes
from odbAccess import openOdb
logging.info("Reading file", filename)
odb = openOdb(filename)
from abapy.misc import dump
logging.info("Reading file", nodes_filename)
lastFrame = odb.steps['Step-1'].frames[-1]

nodes = []
coordinates = {}
with open(nodes_filename, 'r') as f:
    for row in csv.reader(f):
        nodes.append([])
        for node in row:
            logging.debug("Extracting coordinates for node", node)
            nodes[-1].append(int(node))
            coordinates[int(node)] = odb.rootAssembly.instances["PART-1-1"].nodes[int(node)-1].coordinates

number_of_points = int(sum(map(len, nodes)))

######## Perform rotation around y centered on reference node

alpha = np.radians(-48.12)

# rotation matrix with 0 on the y axis because that component doesn't have to be modified
transformation_matrix = np.array([[ np.cos(alpha), 0, np.sin(alpha) ],
                                  [             0, 0,             0 ],
                                  [-np.sin(alpha), 0, np.cos(alpha) ]])

# rotation around y centered on reference node
for macro in coordinates:
    ref = macro[0] # reference node
    for node in macro:
        node += np.dot(transformation_matrix, node - ref)
    
######## Extract displacement at the points
rounded_coordinates = [np.around(c, decimals=3) for c in flatten_list_of_lists(coordinates)]
logging.debug(rounded_coordinates[:3])

assert len(flatten_list_of_lists(coordinates)) == 64
session.Path(name='Path-A', type=POINT_LIST, 
    expression=rounded_coordinates)
pth = session.paths['Path-A']

U = {}
components = ["U1", "U2", "U3"]
for component in components:
    session.viewports['Viewport: 1'].setValues(displayedObject=odb) 

    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
            variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, component))

    session.XYDataFromPath(name='XYData', path=pth, includeIntersections=False,
        projectOntoMesh=True, pathStyle=PATH_POINTS, numIntervals=10,
        projectionTolerance=0.01, shape=DEFORMED, labelType=SEQ_ID)
    U[component] = [x[1] for x in session.xyDataObjects['XYData']]
    logging.debug("Lenght of %s: %d", component, len(U[component]))
    assert len(U[component]) == number_of_points, \
       "Length of component {} is {} instead of {}".format(component, len(U[component]), number_of_points)
######## Rotate the displacement back

# not implemented yet

######## Write the displacements to disk

with open('U.csv', 'w') as csvfile:
    fieldnames = ['node'] + components
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    i = 0
    for macro in nodes:
        for node in macro:
            logging.debug(node, i)
            writer.writerow({'node': node,
                             'U1': U['U1'][i],
                             'U2': U['U2'][i],
                             'U3': U['U3'][i],
                            })
            i = i + 1