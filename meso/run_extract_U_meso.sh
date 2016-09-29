module load abaqus
for filename in $@
do
    MESO_FILENAME=$filename abq6145 viewer noGUI=extract_U_meso.py
done
