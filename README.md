ECSS interpolation scripts
=========================

## How to run on Comet

### Download of the software

* download the software
        
        git clone https://github.com/zonca/ecss-interpolation-scripts

* update to a new version (this will fail if you have local modifications)

        git pull https://github.com/zonca/ecss-interpolation-scripts

### Macro

* Extract the coordinates, rotate them and extract displacements rotated back with `extract_Macro_displacements`, edit the file first to choose the input `odb` and the angle:

        module load abaqus
        abq6145 viewer noGUI=extract_Macro_displacements.py

* Results: see the `results_macro` folder

### Meso

* Run interpolation of each section of the macro independently
* Modified the interpolation script to read automatically the rotated displacements, the only difference is that the section number instead of being 2747 is 0, the new id is based on the row in the `right_femur_nodes.csv` and `left_femur nodes.csv`.
* `interpMaMeO_NewMeso2cei_2747_May13,2016_wCom.py` takes 6 arguments: `input_meso.inp new_file.inp upmult_factor nodecheck.inp rotated_U.rpt section_id`
* run `meso/run_interp.sh` to run create the 16 models
