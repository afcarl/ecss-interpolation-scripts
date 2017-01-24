ECSS interpolation scripts
=========================

## How to run on Comet

### Requirements

* Python 3 installation with `pandas` to run the Python scripts (except the ones that are executed by abaqus, they use a Python 2 version distributed with abaqus)


Location on Comet:

    /home/zonca/ascenzi/openodb
    
Location of data files on SCRATCH on Comet:

    /oasis/scratch/comet/zonca/temp_project/ascenzi
    
  

### Download of the software

* download the software
        
        git clone https://github.com/zonca/ecss-interpolation-scripts

* update to a new version (this will fail if you have local modifications)

        git pull https://github.com/zonca/ecss-interpolation-scripts

### First step: Extract displacements from the Macro Model

* Edit `extract_Macro_displacements.py`, edit the top and change the `filename` of the input model, for example `lgtd4-SI91pss_newversion.odb`, `nodes_filename` for the csv file that lists all of the node ids for each section, for example `left_femur_nodes.csv`, then set the rotation `alpha_degrees` and the frame number `frame_num`.

* Run it through abaqus:

        module load abaqus
        abq6145 viewer noGUI=extract_Macro_displacements.py

* Results: see the `results_macro` folder, it will include the `U.rpt` files for the displacements and `U_rotated_back.rpt` after the rotation. 

        [zonca@comet-ln2 openodb]$ ls results_macro/*/U_r*.rpt
        results_macro/left_femur/U_rotated_back.rpt  results_macro/right_femur/U_rotated_back.rpt

### Second step: Interpolate displacements to the Meso models, add material properties, run Abaqus jobs, extract Meso displacements

Everything in this section is inside the `meso` folder

#### Interpolation

First we want to run the interpolation script of each section of the macro independently

I modified the interpolation script to read automatically the rotated displacements, the only difference is that the section number instead of being 2747 is 0, the new id is based on the row in the `right_femur_nodes.csv` and `left_femur nodes.csv`.

Now the interpolation script `interpMaMeO_NewMeso2cei_2747_May13,2016_wCom.py` takes 6 arguments: `input_meso.inp new_file.inp upmult_factor nodecheck.inp rotated_U.rpt section_id`

The script will read displacements from `../results_macro/[left,right]_femur/U_rotated_back.rpt` created in the section above
It will also read material properties from `Material_prop _for_elemRightLleftfemur - May 27, 2016.txt`.

Procedure:

* run `run_interp.sh` to run the interpolation to create the 16 models, this will create all the `.inp` files in the current folder

#### Run abaqus

We want to submit 16 independent jobs to the scheduler on Comet to execute abaqus on all the `.inp` models, we have a slurm template `sbatch_meso_template.slrm` which is used by the Python script `submit_meso_jobs.py` to create and submit the jobs.

Procedure:

* run `python submit_meso_jobs.py amodel.inp` to run a single model or `python submit_meso_jobs.py *.inp` to run all models
* this will save all the output `.odb` files in the `meso` folder

#### Extract displacements

Displacements are extracted by the script `extract_U_meso.py` and is executed with `run_extract_U_meso.sh`

Procedure:

* Run `run_extract_U_meso.sh *.odb` to extract the displacements from all the models
* The displacements for each `.odb` will be saved as `_U.rpt`, for example `NewMeso_May8_2016_left_section_1.odb` -> `NewMeso_May8_2016_left_section_1_U.rpt`

### Third Step: Interpolate Meso displacements to Micro Models, add material properties, run Abaqus jobs, extract displacements, write summary Excel document

Everything in this section is in the `micro` folder

#### Interpolation

Now interpolation is performed in 2 stages, `interMeMi3m.py` creates a `.inp` model file with no material properties, so this needs to be run just once.

This can be executed by running the `run_interp.sh` script uncommenting the lines:

    python interMeMi3m.py $side $section $model
    python interp2.py
    
and commenting out the line about material properties:

    #python inject_material_properties.py $side $section $model
    
This is a very time consuming process and takes several hours.

The output of this stage is a set of `.inp` files in the current folder with interpolated displacements and a placeholder for the material properties.

In case of 2 Micro models, the number of `.inp` should be 28, 7 section * 2 sides * 2 Micro models.

#### Inject material properties

The second stage is to add the material properties, this is very quick, so this technique allows us to test very quickly different material properties.

This can be executed by running the `run_interp.sh` script commenting the lines:

    #python interMeMi3m.py $side $section $model
    #python interp2.py
    
and uncommenting the line about material properties:

    python inject_material_properties.py $side $section $model
    
We can also modify the script `inject_material_properties.py` to choose the correct material properties file, for example `Material properties micro iso.txt`.

This will write all the output `.inp` files in the `s/` subfolder, which is supposed to be a symlink to the SCRATCH filesystem.

#### Run abaqus

Running abaqus is exactly the same as for Meso, infact first thing we want to symlink the `sbatch_meso_template.slrm` and the `submit_meso_jobs.py` in the `s/` folder.

Then we can submit all the jobs with `python submit_meso_jobs.py *.inp` **inside the `s/` folder**.

This will create all the outputs in the `s/` folder.

#### Extract displacements

`extract_S.py` extracts the displacements for each region of interest as defined inside the `ext_set.py` file into `rpt` files inside dedicated folders, for example: `outputs_S_NewMicro5um_May8_2016_left_section_0`

This can be executed by running the shell script `run_extract_S.sh *.odb` inside the `s/` folder (needs symlinks first).

#### Create Excel summary

Run `python create_S_excel.py` in the `micro` folder to loop through all of the sections and different regions and create a summary excel file in the current folder.
