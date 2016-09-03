import csv
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
    coordinates = {}
    with open(nodes_filename, 'r') as f:
        for row in csv.reader(f):
            nodes.append([])
            for node in row:
                logging.debug("Extracting coordinates for node", node)
                nodes[-1].append(int(node))
                coordinates[int(node)] = odb.rootAssembly.instances["PART-1-1"].nodes[int(node)-1].coordinates
    return nodes, coordinates
