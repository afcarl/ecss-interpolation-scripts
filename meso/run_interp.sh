for i in `seq 0 6`
do
    for side in left
    do
        python interpMaMeO_NewMeso2cei_2747_May13,2016_wCom.py NewMeso_May8,2016_nuovo2.inp NewMeso_May8_2016_${side}_section_${i}.inp 1 nodecheck_${side}_femur_$i.inp ${side} $i
    done
done
