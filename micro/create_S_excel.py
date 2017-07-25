import pandas as pd
import sys
from ext_set import s
from glob import glob

for side in ["left", "right"]: # different file
    for set_tag in ["ext", "bri"]:
        for model in ["5um", "6um"]: # different sheet
            #writer = pd.ExcelWriter('S_july17_NewMicro_May8_2016_{}.xlsx'.format("_".join([side, set_tag, model])))
            output_filename = 'S_july17_NewMicro_May8_2016_{}.csv'.format("_".join([side, set_tag, model]))
            S = []
            for section in range(0,7):
                S_section = []
                fol = "s/output_july17/outputs_S_july17_NewMicro{model}_May8_2016_{side}_section_{section}/".format(side=side, model=model,section=section)
                print("****FOLDER:", fol)

                for region in ["CEFM1", "CODS1"]:

                    filenames = glob(fol + "*{}*{}*.rpt".format(set_tag, region))
                    for filename in filenames:
                        print(filename)

                        number_of_nodes = int(filename.split(".")[0].split("_")[-1])
                        S_section.append(pd.read_csv(filename,
                                skiprows=22,nrows=number_of_nodes,
                                delim_whitespace=True, header=None, skip_blank_lines=True, 
                                skipinitialspace=True,index_col=0,usecols=[0,9,10,11],names=["node","S11-{}".format(section),"S22-{}".format(section),"S33-{}".format(section)])
                                )
                        print("section length", len(S_section[-1]))
                S.append(pd.concat(S_section))
                
            tot = S[0].join(S[1:])
            print("tot", len(tot), len(tot.columns), tot.columns)
            print("to_excel")
            tot.to_csv(output_filename)
            print("Saving")
