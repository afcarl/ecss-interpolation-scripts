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
