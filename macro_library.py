import csv
import numpy as np
import logging

def flatten_list_of_lists(l):
    return [item for sublist in l for item in sublist]

def read_odb_coordinates(nodes_filename, odb):
    """Read coordinates from Abaqus odb files

    Returns
    -------
    nodes : list of lists of integers
        each list is a Macro where the first node is the reference node,
        it contains the ID of all nodes
    coordinates: dictionary
        keys are ID of nodes, values arrays of coordinates extracted
    """
    nodes = []
    coordinates = []
    with open(nodes_filename, 'r') as f:
        for row in csv.reader(f):
            nodes.append([])
            coordinates.append([])
            for node in row:
                logging.debug("Extracting coordinates for node", node)
                nodes[-1].append(int(node))
                coordinates[-1].append(odb.rootAssembly.instances["PART-1-1"].nodes[int(node)-1].coordinates)
    return nodes, coordinates

def rotate_coordinates(alpha_degrees, coordinates):

    alpha = np.radians(alpha_degrees)

    rotated_coordinates = []
    # rotation of the relative vector between node and ref_node around the y axis
    for macro in coordinates:
        ref_node_coordinates = macro[0] # reference node
        rotated_coordinates.append([])
        for node_coordinates in macro:
            delta = node_coordinates - ref_node_coordinates # relative position
            rotated_coordinates[-1].append(np.array([
                ref_node_coordinates[0] + np.cos(alpha) * delta[0] + np.sin(alpha) * delta[2],
                node_coordinates[1],
                ref_node_coordinates[2] - np.sin(alpha) * delta[0] + np.cos(alpha) * delta[2],
            ]))

    return rotated_coordinates

def rotate_displacements_back(alpha_degrees, U):
    alpha = np.radians(alpha_degrees)
    transformation_matrix = np.array([[ np.cos(-alpha), 0, np.sin(-alpha) ],
                                      [              0, 1,             0 ],
                                      [-np.sin(-alpha), 0, np.cos(-alpha) ]])
    rotated_displacements = []
# rotation around y
    for macro in U:
        rotated_displacements.append([])
        for node_U in macro:
            rotated_displacements[-1].append(np.dot(transformation_matrix, np.array(node_U)))
    return rotated_displacements

def write_rpt(filename, data, nodes, fields=["x", "y", "z"]): 
    with open(filename, 'w') as csvfile:
        fieldnames = ['node'] + fields
        writer = csv.DictWriter(csvfile, delimiter="\t", fieldnames=fieldnames)

        writer.writeheader()
        for macro, macro_data in zip(nodes, data):
            for node, node_data in zip(macro, macro_data):
                writer.writerow({'node': node,
                                 fields[0]: node_data[0],
                                 fields[1]: node_data[1],
                                 fields[2]: node_data[2],
                                })
