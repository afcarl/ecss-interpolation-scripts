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
projection_tolerance = 0.0000001
test_coordinates = True
########

logging.basicConfig(filename=filename + ".log",level=logging_level, filemode="w")

def flatten_list_of_lists(l):
    return [item for sublist in l for item in sublist]
    
######## Extract coordinates from the odb file and store it in nodes
from odbAccess import openOdb
logging.info("Reading file", filename)
odb = openOdb(filename)
logging.info("Reading file", nodes_filename)
#lastFrame = odb.steps['Step-1'].frames[-1]
#session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=6)

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

if test_coordinates:
    coordinates[3457] = np.array([0.207,0.218,0.223])                                                                                                                                                                                                                                            
    coordinates[3459] = np.array([0.210,0.218,0.223])                                                                                                                                                                                                                                                                                                        
    coordinates[3714] = np.array([0.210,0.218,0.226])                                                                                                                                                                                                                                                                                                        
    coordinates[3713] = np.array([0.207,0.218,0.226])                                                                                                                                                                                                                                                                                                        
    coordinates[3435] = np.array([0.207,0.215,0.223])                                                                                                                                                                                                                                                                                                        
    coordinates[3437] = np.array([0.210,0.215,0.223])                                                                                                                                                                                                                                                                                                        
    coordinates[3689] = np.array([0.210,0.215,0.226])                                                                                                                                                                                                                                                                                                        
    coordinates[3688] = np.array([0.207,0.215,0.226])                                                                                                                                                                                                                                                                                                        
    coordinates[2801] = np.array([0.201,0.224,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2803] = np.array([0.204,0.224,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[3033] = np.array([0.204,0.224,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[3032] = np.array([0.201,0.224,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2781] = np.array([0.201,0.221,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2783] = np.array([0.204,0.221,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[3013] = np.array([0.204,0.221,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[3012] = np.array([0.201,0.221,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2780] = np.array([0.198,0.221,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2781] = np.array([0.201,0.221,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[3012] = np.array([0.201,0.221,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[3011] = np.array([0.198,0.221,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2758] = np.array([0.198,0.218,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2759] = np.array([0.201,0.218,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2990] = np.array([0.201,0.218,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2989] = np.array([0.198,0.218,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2758] = np.array([0.198,0.218,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2759] = np.array([0.201,0.218,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2990] = np.array([0.201,0.218,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2989] = np.array([0.198,0.218,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2739] = np.array([0.198,0.215,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2741] = np.array([0.201,0.215,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2970] = np.array([0.201,0.215,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2969] = np.array([0.198,0.215,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2947] = np.array([0.195,0.212,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2949] = np.array([0.198,0.212,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[3177] = np.array([0.198,0.212,0.220])                                                                                                                                                                                                                                                                                                        
    coordinates[3175] = np.array([0.195,0.212,0.220])                                                                                                                                                                                                                                                                                                        
    coordinates[2946] = np.array([0.195,0.209,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2948] = np.array([0.198,0.209,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[3176] = np.array([0.198,0.209,0.220])                                                                                                                                                                                                                                                                                                        
    coordinates[3174] = np.array([0.195,0.209,0.220])                                                                                                                                                                                                                                                                                                        
    coordinates[2801] = np.array([0.201,0.224,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2803] = np.array([0.204,0.224,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[3033] = np.array([0.204,0.224,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[3032] = np.array([0.201,0.224,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2781] = np.array([0.201,0.221,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2783] = np.array([0.204,0.221,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[3013] = np.array([0.204,0.221,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[3012] = np.array([0.201,0.221,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2781] = np.array([0.201,0.221,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2783] = np.array([0.204,0.221,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[3013] = np.array([0.204,0.221,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[3012] = np.array([0.201,0.221,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2759] = np.array([0.201,0.218,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2763] = np.array([0.204,0.218,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2991] = np.array([0.204,0.218,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2990] = np.array([0.201,0.218,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2759] = np.array([0.201,0.218,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2763] = np.array([0.204,0.218,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2991] = np.array([0.204,0.218,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2990] = np.array([0.201,0.218,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2741] = np.array([0.201,0.215,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2761] = np.array([0.204,0.215,0.214])                                                                                                                                                                                                                                                                                                        
    coordinates[2973] = np.array([0.204,0.215,0.217])                                                                                                                                                                                                                                                                                                        
    coordinates[2970] = np.array([0.201,0.215,0.217]) 

#coordinates[2759] = np.array([0.201, 0.218, 0.214])
#coordinates[2970] = np.array([0.201, 0.215, 0.217])
with open('coordinates_before_rotation.csv', 'w') as csvfile:
    fieldnames = ['node'] + ["x", "y", "z"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for macro in nodes:
        for node in macro:
            writer.writerow({'node': node,
                             'x': coordinates[node][0],
                             'y': coordinates[node][1],
                             'z': coordinates[node][2],
                            })

######## Perform rotation around y centered on reference node

alpha = np.radians(-48.12)

# rotation matrix with 0 on the y axis because that component doesn't have to be modified
transformation_matrix = np.array([[ np.cos(alpha), 0, np.sin(alpha) ],
                                  [             0, 0,             0 ],
                                  [-np.sin(alpha), 0, np.cos(alpha) ]])

rotated_coordinates = {}
# rotation around y centered on reference node
for macro in nodes:
    ref_node = macro[0] # reference node
    for node in macro:
        rotated_coordinates[node] = coordinates[node] + \
             np.dot(transformation_matrix, coordinates[node] - coordinates[ref_node])

with open('coordinates_after_rotation.csv', 'w') as csvfile:
    fieldnames = ['node'] + ["x", "y", "z"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for macro in nodes:
        for node in macro:
            writer.writerow({'node': node,
                             'x': rotated_coordinates[node][0],
                             'y': rotated_coordinates[node][1],
                             'z': rotated_coordinates[node][2],
                            })

######## Extract displacement at the points
#rounded_coordinates = [np.around(rotated_coordinates[n], decimals=3) for n in flatten_list_of_lists(nodes)]
rounded_coordinates = [rotated_coordinates[n] for n in flatten_list_of_lists(nodes)]
logging.debug(rounded_coordinates[:4])
session.Path(name='Path-A', type=POINT_LIST, expression=rounded_coordinates)
pth = session.paths['Path-A']

U = {}
components = ["U1", "U2", "U3"]
for component in components:
    session.viewports['Viewport: 1'].setValues(displayedObject=odb) 
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=6)

    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
            variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, component))

    session.XYDataFromPath(name='XYData-' + component, path=pth, includeIntersections=False,
        projectOntoMesh=True, pathStyle=PATH_POINTS, numIntervals=10,
        projectionTolerance=projection_tolerance, shape=DEFORMED, labelType=TRUE_DISTANCE)
    U[component] = [x[1] for x in session.xyDataObjects['XYData-' + component]]
    logging.debug("Lenght of %s: %d", component, len(U[component]))

    if len(U[component]) != number_of_points:
        logging.error("Length of component {} is {} instead of {}".format(component,
                  len(U[component]), number_of_points))

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