#!/bin/bash

# A little script to combine all the subjects in a sublist
# and show their data coverage in standard space

sublist=$1
data_dir=$2
output_dir=$3

overlay_file=${output_dir}/masks_overlay.nii.gz
bins_overlay_file=${output_dir}/masks_overlay_binned

subs=(`cat ${sublist}`)

n=${#subs[@]}

fslmaths ${data_dir}/${subs[0]}.feat/reg_standard/mask.nii.gz -mul 0 ${overlay_file}
fslmaths ${overlay_file} -mul 0 ${bins_overlay_file}

for sub in ${subs[@]}; do
    fslmaths ${overlay_file} -add ${data_dir}/${sub}.feat/reg_standard/mask.nii.gz ${overlay_file}
done

fslmaths ${overlay_file} -bin ${bins_overlay_file}.nii.gz

percents=(000 050 090 100 101)

i=0
until [[ ${percents[$i]} == 101 ]]; do

    let j=${i}+1

    ll=(`echo "${percents[$i]} * $n / 100" | bc -l`)

    fslmaths ${overlay_file}.nii.gz -thr ${ll} -bin -mul ${j} ${bins_overlay_file}_${percents[$i]}.nii.gz
    
    let i=${i}+1

done

for f in `ls -d ${output_dir}/masks_overlay_binned_???.nii.gz`; do
    fslmaths ${bins_overlay_file} -max ${f} ${bins_overlay_file}
done