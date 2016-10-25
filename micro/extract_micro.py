import visualization
from abaqus import *
from abaqusConstants import *
import displayGroupOdbToolset as dgo
import os

filename = os.environ["ODB_FILENAME"]
folder = "outputs_" + filename.replace(".odb","")
try:
    os.mkdir(folder)
except:
    pass

from odbAccess import openOdb
o1 = openOdb(filename)

session.viewports['Viewport: 1'].setValues(displayedObject=o1)
leaf = dgo.LeafFromElementSets(elementSets=('MIDSECTION', ))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
leaf = dgo.LeafFromElementSets(elementSets=('WarnElemDistorted', ))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.remove(leaf=leaf)
leaf = dgo.LeafFromElementSets(elementSets=('WarnElemDistorted', ))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.remove(leaf=leaf)
odb = session.odbs[filename]

out_filename = os.path.join(folder, filename.replace(".odb", '_midsection'))
session.writeFieldReport(fileName=out_filename + ".rpt", append=ON, 
    sortItem='Element Label', odb=odb, step=0, frame=1, 
    outputPosition=ELEMENT_NODAL, variable=(('S', INTEGRATION_POINT), ))
session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
session.printToFile(fileName=out_filename + ".tiff", format=TIFF, 
    canvasObjects=(session.viewports['Viewport: 1'], ))

out_filename += "_EXT"
leaf = dgo.LeafFromElementSets(elementSets=('CEFM1.HEBRI', 'CEFM2.HEBRI', 
    'CODS1.HEBRI', 'CODS2.HEBRI', ))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.intersect(leaf=leaf)
leaf = dgo.LeafFromElementSets(elementSets=('CEFM1.CEML', 'CEFM2.CEML', 
    'CODS1.CEML', 'CODS2.CEML', ))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.remove(leaf=leaf)
odb = session.odbs[filename]
session.writeFieldReport(fileName=out_filename + '.rpt', append=ON, 
    sortItem='Element Label', odb=odb, step=0, frame=1, 
    outputPosition=ELEMENT_NODAL, variable=(('S', INTEGRATION_POINT), ))
session.printToFile(fileName=out_filename + '.tiff', format=TIFF, 
    canvasObjects=(session.viewports['Viewport: 1'], ))
