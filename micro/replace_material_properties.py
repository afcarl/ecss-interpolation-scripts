import sys
import os
import pandas as pd

side = sys.argv[1]
section = int(sys.argv[2])
model = sys.argv[3]

#str(input("\033[32mInput the MESO file name with the .inp extension: \033[0m: "))
Xmeso_filename = "../meso/NewMeso_May8_2016_{side}_section_{section}.inp".format(side=side, section=section)

Xmicro_DUMP = os.path.basename(Xmeso_filename.replace("Meso", "Micro" + model))

# zonca: replace material
material = pd.read_csv("../meso/Material_prop _for_elemRightLleftfemur - May 27, 2016.txt")

M = material[material["Femur"] == side.capitalize()].iloc[section]["ElasticModulus[Pa]"]

with open("Material properties micro.txt", "r") as f:
    materials = f.read().strip()

materials = materials.format(M=M, Mdiv2=M/2., M3div2=M*3/2.)

with open("Material properties micro switched.txt", "r") as f:
    materials_switched = f.read().strip()

materials_switched = materials_switched.format(M=M, Mdiv2=M/2., M3div2=M*3/2.)


with open(Xmicro_DUMP, "r") as f:
    all_finalfile = f.read()

all_finalfile = all_finalfile.replace(materials, materials_switched)

with open("out_" + Xmicro_DUMP, "w") as f:
    f.write(all_finalfile)
