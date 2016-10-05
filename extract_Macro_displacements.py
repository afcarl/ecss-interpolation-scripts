from __future__ import division, print_function
import sys

import numpy as np
import logging

## Abaqus CAE imports
import visualization
from abaqus import *
from abaqusConstants import *

######## CONFIGURATION OPTIONS
#Choose settings for right or left femur
filename = "rgtd5-SI91pss.odb"
nodes_filename = "right_femur_nodes.csv"
alpha_degrees = -48.12
frame_num = 6

#filename = "lgtd4-SI91.odb"
#nodes_filename = "left_femur_nodes.csv"
#alpha_degrees = 61.39
#frame_num = 4

#For both femurs
projection_tolerance = 0.0000001
#logging.DEBUG for verbose output, logging.INFO intermediate, logging.ERROR for quiet
logging_level = logging.DEBUG
########

######## Data structures

# this script has different data structures related to the nodes, all have the same shape,
# very similar to the "right_femur_nodes.csv" file, i.e. they are list of lists, each
# element of the outer list is a row in the file, so it contains all the nodes of the same group
# elements of the inner list contain the data for each node.
# for example it is an integer of the Abaqus ID for `nodes` and a Numpy array with 3 components
# for `coordinates`, `rotated_coordinates`, `U` and `U_rotated_back`.

logging.basicConfig(filename=filename + ".log",level=logging_level, filemode="w")

######## Extract coordinates from the odb file and store it in nodes
from odbAccess import openOdb
logging.info("Reading file", filename)
odb = openOdb(filename)
logging.info("Reading file", nodes_filename)

from macro_library import read_odb_coordinates, flatten_list_of_lists, write_rpt, rotate_coordinates, rotate_displacements_back

nodes, coordinates = read_odb_coordinates(nodes_filename, odb)
number_of_points = int(sum(map(len, nodes)))
write_rpt('coordinates_before_rotation.rpt', coordinates, nodes)

######## Perform rotation around y centered on reference node
rotated_coordinates = rotate_coordinates(alpha_degrees, coordinates)
write_rpt('coordinates_after_rotation.rpt', rotated_coordinates, nodes)

session.viewports['Viewport: 1'].setValues(displayedObject=odb)
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=0, frame=frame_num)

######## Extract displacement at the points
list_of_rotated_coordinates = flatten_list_of_lists(coordinates)
session.Path(name='Path-A', type=POINT_LIST, expression=list_of_rotated_coordinates)
pth = session.paths['Path-A']

# Create empty `U`
U = []
for macro in nodes:
    U.append([])
    for node in macro:
        U[-1].append([])

# Extract displacements from the odb and save them in U
components = ["U1", "U2", "U3"]
for component in components:

    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
            variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, component))

    session.XYDataFromPath(name='XYData-' + component, path=pth, includeIntersections=False,
        projectOntoMesh=False, pathStyle=PATH_POINTS, numIntervals=10,
        projectionTolerance=projection_tolerance, shape=DEFORMED, labelType=TRUE_DISTANCE)

    x0 = session.xyDataObjects['XYData-'+component]
    session.writeXYReport(fileName=component + '.rpt', xyData=(x0, ))

    #xQuantity = visualization.QuantityType(type=NUMBER)
    #yQuantity = visualization.QuantityType(type=DISPLACEMENT)
    #session.xyDataObjects['XYData-' + component].setValues(axis1QuantityType=xQuantity, axis2QuantityType=yQuantity)

    all_U_for_one_component = [x[1]*1e6 for x in session.xyDataObjects['XYData-' + component]]
    i = 0
    for macro in U:
        for node_U in macro:
            node_U.append(all_U_for_one_component[i])
            i = i + 1
            
    logging.debug("Lenght of %s: %d", component, len(all_U_for_one_component))

    if len(all_U_for_one_component) != number_of_points:
        logging.error("Length of component {} is {} instead of {}".format(component,
                  all_U_for_one_component, number_of_points))

######## Write the displacements to disk

write_rpt('U.rpt', U, nodes, fields=components)

######## Rotate the displacement back

# no need to provide -alpha here, sign is changed inside the function
rotated_U = rotate_displacements_back(alpha_degrees, U)

write_rpt('U_rotated_back.rpt', rotated_U, nodes, fields=components)
