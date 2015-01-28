#!/usr/bin/env python

#=============================================================================
# IMPORTS
#=============================================================================
import os
import numpy as np
import scipy.io as sio
from glob import glob
import pandas as pd

import nibabel as nib
from surfer import Brain

import itertools as it
from scipy.stats.stats import linregress

import matplotlib.pylab as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec

import argparse

#=============================================================================
# FUNCTIONS
#=============================================================================
#==============================================================================
def setup_argparser():
    '''
    Read in arguments from command line and provide a little help
    '''
    
    # Build a basic parser.
    help_text = ('Visualize a volume in MNI space onto a freesurfer surface')
    
    sign_off = 'Author: Kirstie Whitaker <kw401@cam.ac.uk>'
    
    parser = argparse.ArgumentParser(description=help_text, epilog=sign_off)
    
    # Now add the arguments
    # Required argument: result_file
    parser.add_argument(dest='result_file', 
                            type=str,
                            metavar='result_file',
                            help='Result .nii.gz file, eg: thresh_zstat1.nii.gz')
    
    # Required argument: surface
    parser.add_argument(dest='surface', 
                            type=str,
                            metavar='surface',
                            help='One of "inflated", "pial" or "white"')
    
    # Optional argument: minimum value
    parser.add_argument('--min_val', 
                            type=float,
                            metavar='min_val',
                            default=None,
                            help='Minimum value for overlay')
                            
    # Optional argument: maximum value
    parser.add_argument('--max_val', 
                            type=float,
                            metavar='max_val',
                            default=None,
                            help='Maximum value for overlay')
                            
    # Optional argument: threshold value
    parser.add_argument('--thr_val', 
                            type=float,
                            metavar='thr_val',
                            default=0,
                            help='Threshold value for overlay')

    # Optional argument: colormap
    parser.add_argument('--cmap', 
                            type=str,
                            metavar='cmap',
                            default='autumn',
                            help='Any matplotlib colormap')
                            
    arguments = parser.parse_args()
    
    return arguments, parser
  
def project_surface(result_file, hemi):

    '''
    VERY helpfully taken from the Pysurfer example gallery
    http://pysurfer.github.io/examples/plot_fmri_activation_volume.html
    
    Parameters
    ----------
    result_file : str
                  3D volume that has continuous values
                  eg: thresh_zstat1.nii.gz
    hemi        : {'lh', 'rh'}
                  string indicating left or right hemisphere
                  
    Returns
    ----------
    zstat       : pysurfer surface
                  Surface projection of result_file to fsaverage
                  brain
    '''
    import os
    from surfer import project_volume_data

    reg_file = os.path.join(os.environ["FREESURFER_HOME"],
                            "average/mni152.register.dat")
    zstat = project_volume_data(result_file, hemi, reg_file)

    return zstat
    
def visualise_surface(zstat, hemi, surface='inflated', min_val=None, max_val=None, thr_val=0, cmap='autumn'):
    '''
    VERY helpfully taken from the Pysurfer example gallery
    http://pysurfer.github.io/examples/plot_fmri_activation_volume.html
    
    Parameters
    ----------
    zstat   : pysurfer surface
                Surface projection of result_file to fsaverage
                brain
    prefix  : save
    hemi    : {'lh', 'rh'}
                string indicating left or right hemisphere
    surface : {'inflated', 'pial', 'white'}    
                string indicating surface view
    min_val : minimum value to be shown 
                (default is to calculate it from the data)
    max_val : maximum value to be shown
                (default is to calculate it from the data)
    thr_val : threshold value
                zero everything below this number
                (default is 0)        
    cmap    : matplotlib colormap
                (default is autumn)
                
    Returns
    ----------
    brain   : current pysurfer visualization window
    '''
    
    """
    Bring up the visualization window.
    """
    brain = Brain("fsaverage", hemi, surface, config_opts={'background':'white'})

    """
    Add zstat as an overlay
    """
    brain.add_data(zstat, min=min_val, max=max_val, thresh=thr_val, colormap=cmap, colorbar=True)
    
    return brain

def save_pngs(brain, prefix):
    """
    Save current visualization as pngs.
    
    Note that this code adds a colorbar to every image.
    
    Parameters
    ----------
    brain     : current pysurfer visualization window
    prefix    : path and prefix to output filenames to which the
                specific view will be added
                    eg: thresh_zstat1 --> thresh_zstat1_medial.png
                                      --> thresh_zstat1_lateral.png

    Creates
    ----------
    two png files with the prefix as define above
    
    """
    views_list = [ 'medial', 'lateral' ]
    
    brain.save_imageset(prefix,
                        views = views_list, 
                        colorbar = range(len(views_list)) )
    
    return brain

def combine_pngs(result_file, surface):

    figsize = (4.5,4)
    fig = plt.figure(figsize = figsize, facecolor='white')

    grid = gridspec.GridSpec(2, 2)
    grid.update(left=0, right=1, top=1, bottom = 0.08, wspace=0, hspace=0)
    
    f_list = [ '{}_{}_{}_{}.png'.format(result_file.strip('.nii.gz'), 'lh', surface, 'lateral'),
                '{}_{}_{}_{}.png'.format(result_file.strip('.nii.gz'), 'rh', surface, 'lateral'),
                '{}_{}_{}_{}.png'.format(result_file.strip('.nii.gz'), 'lh', surface, 'medial'),
                '{}_{}_{}_{}.png'.format(result_file.strip('.nii.gz'), 'rh', surface, 'medial') ]

                           
    for g_loc, f in zip(grid, f_list):
        ax = plt.Subplot(fig, g_loc)
        fig.add_subplot(ax)
        img = mpimg.imread(f)
        if 'lateral' in f:
            img_cropped = img[58:598,60:740,:]
        else:
            img_cropped = img[18:628,15:785,:]
        ax.imshow(img_cropped, interpolation='none')
        ax.set_axis_off()

    grid_cbar = gridspec.GridSpec(1,1)
    grid_cbar.update(left=0, right=1, top=0.08, bottom=0, wspace=0, hspace=0)
    ax = plt.Subplot(fig, grid_cbar[0])
    fig.add_subplot(ax)
    img = mpimg.imread(f)
    img_cbar = img[605:,:]
    ax.imshow(img_cbar, interpolation='none')
    ax.set_axis_off()
    
    filename = '{}_{}_{}.png'.format(result_file.strip('.nii.gz'), surface, 'combined')
    print filename
    fig.savefig(filename, bbox_inches=0, dpi=300)

#=============================================================================
# READY GO!
#=============================================================================
# Read in the arguments from argparse
arguments, parser = setup_argparser()

result_file = arguments.result_file
surface = arguments.surface
min_val = arguments.min_val
max_val = arguments.max_val
thr_val = arguments.thr_val
cmap = arguments.cmap

# Define the prefix as just the result filename 
# without its extension followed by the surface used
prefix = result_file.strip('.nii.gz')

hemi_list = [ 'lh', 'lh', 'rh' ]

for hemi in hemi_list:
    prefix = '{}_{}_{}'.format(result_file.strip('.nii.gz'), hemi, surface)

    zstat = project_surface(result_file, hemi)
    brain = visualise_surface(zstat, 
                               hemi, 
                               surface, 
                               min_val=min_val, 
                               max_val=max_val, 
                               thr_val=thr_val,
                               cmap=cmap)
    prefix = '{}_{}_{}'.format(result_file.strip('.nii.gz'), hemi, surface)
    brain = save_pngs(brain, prefix)

combine_pngs(result_file, surface)

#=============================================================================
# THE END!
#=============================================================================