module load abaqus
for filename in $@
do
    ODB_FILENAME=$filename abq6145 viewer noGUI=extract_micro.py
done
