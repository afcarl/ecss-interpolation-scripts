import pandas as pd
from ext_set import s
from glob import glob

for side in ["left", "right"]: # different file
    writer = pd.ExcelWriter('S_NewMicro_May8_2016_{}.xlsx'.format(side))
    for set_tag in ["ext", "bri"]:
        for model in ["5um", "6um"]: # different sheet
            S = []
            for section in range(7):
                S_section = []
                for region in ["CEFM1", "CODS1"]:
                    fol = "s/outputs_S_NewMicro{model}_May8_2016_{side}_section_{section}/".format(side=side, model=model,section=section)
                    filenames = glob(fol + "*{}*{}*.rpt".format(set_tag, region))
                    assert len(filenames) == 1
                    filename = filenames[0]
                    print(filename)
                    number_of_nodes = int(filename.split(".")[0].split("_")[-1])
                    S_section.append(pd.read_csv(filename,
                            skiprows=22,nrows=number_of_nodes,
                            delim_whitespace=True, header=None, skip_blank_lines=True, 
                            skipinitialspace=True,index_col=0,usecols=[0,9,10,11],names=["node","S11-{}".format(section),"S22-{}".format(section),"S33-{}".format(section)])
                            )
                S.append(pd.concat(S_section))
                
            S[0].join(S[1:]).to_excel(writer,set_tag + "_" + model)
    writer.save()
