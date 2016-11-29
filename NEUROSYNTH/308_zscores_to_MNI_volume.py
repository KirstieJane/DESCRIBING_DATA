#!/usr/bin/env python

import nibabel as nib
import numpy as np
import matplotlib.pylab as plt

template_file = 'VOLUME_MAPS/500_aparc_MNI.nii.gz'
pls_file = 'PLS_0.txt'

def convert_308text_to_volume(template_file, pls_file):
    # Load in the PLS scores
    pls_scores = np.loadtxt(pls_file)

    # Read in the template file (in MNI space)
    img = nib.load(template_file)

    # Get the data
    data = img.get_data()

    # Remove all the subcortical regions and set to 0
    data_pls = data - 41.0
    data_pls[data_pls<0] = 0

    # Loop through the pls scores for each region and
    # replace the region in the template with this score
    for i, score in enumerate(pls_scores):
        data_pls[data_pls==(i+1)] = score

    # Set any -99s to 0
    data_pls[data_pls==-99]=0

    # Save the output file
    img_new = nib.Nifti1Image(data_pls, img.get_affine())
    nib.save(img_new, 'VOLUME_MAPS/{}.nii.gz'.format(pls_file.strip('.txt')))

# AAAAAAND GO
convert_308text_to_volume(template_file, pls_file)
