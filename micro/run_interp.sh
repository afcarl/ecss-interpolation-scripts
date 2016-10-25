#for side in right left
for side in left
do
    for section in `seq 1 6`
    #for section in `seq 0 0`
    do
        for model in 6um 5um
        #for model in 6um
        do
            python interMeMi3m.py $side $section $model
            python interp2.py
            python inject_material_properties.py $side $section $model
        done
    done
done
