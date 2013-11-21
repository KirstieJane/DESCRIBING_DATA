#!/bin/bash

#=============================================================================
# A little script to combine all the subjects in a sublist
# and show their data coverage in standard space
#
# Written by Kirstie Whitaker
# kw401@cam.ac.uk
#=============================================================================

# Define the usage
function usage {
    echo "USAGE: ./masks_overlay.sh <data_dir> <subject_path_list> <output_dir>"
    echo "    <data_dir> - directory containing feat directories"
    echo "    <subject_path_list> - list of paths to individual subject's feat directories"
    echo "         (but excluding the .feat extension) inside the data directory"
    echo "        eg: 1235"
    echo "    <output_dir> - location of output binned data"
}    

# Assign the arguments and check that they're there
data_dir=$1
subject_path_list=$2
output_dir=$3

# Here's where you can manually set the edges of the percent bins
# if you want to change them.
# Make sure they are all 3 digits long and that the last two are 
# 100 and 101 respectively
percents=(050 090 100 101)

if [[ ! -d ${data_dir} ]]; then
    echo "DATA DIRECTORY DOES NOT EXIST"
    print_usage=1
fi

if [[ ! -f ${subject_path_list} ]]; then
    echo "SUBJECT PATH LIST FILE DOES NOT EXIST"
    print_usage=1
fi

if [[ ${print_usage} == 1 ]]; then
    usage
    exit
fi

# Make the output directory
mkdir -p ${output_dir}

# Assign the output names
overlay_file=${output_dir}/masks_overlay.nii.gz
bins_overlay_file=${output_dir}/masks_overlay_binned

# Read in the subjects
subs=(`cat ${sublist}`)

# Find the number of subjects
n=${#subs[@]}

# Create empty file for the overlay_file and bins_overlay_file 
# that are the right dimensions but empty
fslmaths ${data_dir}/${subs[0]}.feat/reg_standard/mask.nii.gz -mul 0 ${overlay_file}
fslmaths ${overlay_file} -mul 0 ${bins_overlay_file}

# Loop through the subs and add the participants on top of each other
for sub in ${subs[@]}; do
    fslmaths ${overlay_file} -add ${data_dir}/${sub}.feat/reg_standard/mask.nii.gz ${overlay_file}
done

# Binarize the overlay_file
fslmaths ${overlay_file} -bin ${bins_overlay_file}.nii.gz

# Start a counter for the lower limit
i=0
# Loop through all the percent bins
until [[ ${percents[$i]} == 101 ]]; do
    
    # While i counts from 0, j counts from 1
    let j=${i}+1

    # Calculate the lower limit
    ll=(`echo "${percents[$i]} * $n / 100" | bc -l`)

    # Threshold the overlay_file at the lower limit and multiply by j
    fslmaths ${overlay_file}.nii.gz -thr ${ll} -bin -mul ${j} ${bins_overlay_file}_${percents[$i]}.nii.gz
    
    let i=${i}+1

done

# Now take the maximum of each of the masks_overlay_binned files
# and add them together to the bins_overlay_file
for f in `ls -d ${output_dir}/masks_overlay_binned_???.nii.gz`; do
    fslmaths ${bins_overlay_file} -max ${f} ${bins_overlay_file}
done

# Done!