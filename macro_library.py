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

# rotation matrix with 0 on the y axis because that component doesn't have to be modified
    transformation_matrix = np.array([[ np.cos(alpha), 0, np.sin(alpha) ],
                                      [             0, 0,             0 ],
                                      [-np.sin(alpha), 0, np.cos(alpha) ]])

    rotated_coordinates = []
# rotation around y centered on reference node
    for macro in coordinates:
        ref_node_coordinates = macro[0] # reference node
        rotated_coordinates.append([])
        for node_coordinates in macro:
            rotated_coordinates[-1].append(ref_node_coordinates + \
                 np.dot(transformation_matrix, node_coordinates - ref_node_coordinates))
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

def write_csv(filename, data, nodes): 
    with open(filename, 'w') as csvfile:
        fieldnames = ['node'] + ["x", "y", "z"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for macro, macro_data in zip(nodes, data):
            for node, node_data in zip(macro, macro_data):
                writer.writerow({'node': node,
                                 'x': node_data[0],
                                 'y': node_data[1],
                                 'z': node_data[2],
                                })
