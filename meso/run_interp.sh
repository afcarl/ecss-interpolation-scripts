for i in `seq 0 7`
do
    python interpMaMeO_NewMeso2cei_2747_May13,2016_wCom.py NewMeso_May8,2016.inp NewMeso_May8_2016_right_section_${i}.inp 1 nodecheck_right_femur_$i.inp ../results_macro/rgtd5-SI91pss/U_rotated_back.rpt $i
    python interpMaMeO_NewMeso2cei_2747_May13,2016_wCom.py NewMeso_May8,2016.inp NewMeso_May8_2016_left_section_${i}.inp 1 nodecheck_left_femur_$i.inp ../results_macro/lgtd4-SI91/U_rotated_back.rpt $i
done
