#!/usr/bin/env python

#=============================================================================
# Created by Kirstie Whitaker
# September 2014
# Contact: kw401@cam.ac.uk
#=============================================================================

#=============================================================================
# IMPORTS
#=============================================================================
import os
import sys
import argparse
import numpy as np

import pandas as pd
import nibabel as nib
from surfer import Brain

import itertools as it

import matplotlib.pylab as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec

import matplotlib.colors as mcolors
import matplotlib.cm as cm

#=============================================================================
# FUNCTIONS
#=============================================================================
def setup_argparser():
    '''
    Code to read in arguments from the command line
    Aso allows you to change some settings
    '''
    # Build a basic parser.
    help_text = ('Plot values on a freesurfer surface')
    
    sign_off = 'Author: Kirstie Whitaker <kw401@cam.ac.uk>'
    
    parser = argparse.ArgumentParser(description=help_text, epilog=sign_off)
    
    # Now add the arguments
    parser.add_argument(dest='roi_file', 
                            type=str,
                            metavar='roi_file',
                            help='roi file containing list of measure values - one for each region - csv format')
                            
    parser.add_argument('--fsaverageid',
                            type=str,
                            metavar='fsaverage_id',
                            help='FSaverage subject id',
                            default='fsaverageSubP')
    
    parser.add_argument('-sd', '--subjects_dir',
                            type=str,
                            metavar='subjects_dir',
                            help='freesurfer subjects dir',
                            default=os.environ["SUBJECTS_DIR"])
                                                        
    parser.add_argument('-c', '--cmap',
                            type=str,
                            metavar='cmap',
                            help='colormap',
                            default='RdBu_r')
###
    parser.add_argument('-cf', '--color_file',
                            type=str,
                            metavar='color_file',
                            help='file containing list of custom colors',
                            default=None)                     
###
    parser.add_argument('--center',
                            action='store_true',
                            help='center the color bar around 0')
                            
    parser.add_argument('-t', '--thresh',
                            type=float,
                            metavar='thresh',
                            help='mask values below this value',
                            default=-98)
                            
    parser.add_argument('-l', '--lower',
                            type=float,
                            metavar='lowerthr',
                            help='lower limit for colorbar',
                            default=None)

    parser.add_argument('-u', '--upper',
                            type=float,
                            metavar='upperthr',
                            help='upper limit for colorbar',
                            default=None)
                            
    
    parser.add_argument('-s', '--surface',
                            type=str,
                            metavar='surface',
                            help='surface - one of "pial", "inflated" or "both"',
                            default='both')
                            
    arguments = parser.parse_args()
    
    return arguments, parser

#------------------------------------------------------------------------------
###
def calc_range(roi_data, l, u, thresh, center):
    # Figure out the min and max for the color bar
    if l == None:
        l = roi_data[roi_data>thresh].min()
        l = np.floor(l*20)/20.0
    if u == None:
        u = roi_data[roi_data>thresh].max()
        u = np.ceil(u*20)/20.0
 
    if center:
        # Make sure the colorbar is centered
        if l**2 < u **2:
            l = u*-1
        else:
            u = l*-1

    return l, u

# could add if cmap = "custom", then l = min(data), u = max(data)    

#------------------------------------------------------------------------------
def plot_surface(vtx_data, subject_id, hemi, surface, subjects_dir, output_dir, prefix, l, u, cmap, thresh):
    """
    This function needs more documentation, but for now
    it is sufficient to know this one important fact:
	For the variable "cmap":
	    If you pass a word that defines a matplotlib
	      colormap (eg: jet, Rd_Bu etc) then the code
	      will use that for the color scheme.
	    If you pass a **list** of colors then you'll
	      just loop through those colors instead. 
    """
    
    # Open up a brain in pysurfer
    brain = Brain(subject_id, hemi, surface,
                  subjects_dir = subjects_dir,
                  config_opts=dict(background="white",
                                   height=665,
                                   width=800))

    # Add your data to the brain
    brain.add_data(vtx_data,
                l, 
                u,
                thresh = thresh,
                colormap=cmap,
                alpha=.8)
    # Save the images for medial and lateral
    # putting a color bar on all of them
    brain.save_imageset(prefix = os.path.join(output_dir, prefix),
                        views = views_list, 
                        colorbar = range(len(views_list)) )

#----------------------------------------------------------------------------- 
def combine_pngs(measure, surface, output_dir):
    '''
    Find four images and combine them into one nice picture
    '''
    figsize = (5,4)
    fig = plt.figure(figsize = figsize, facecolor='white')

    grid = gridspec.GridSpec(2, 2)
    grid.update(left=0, right=1, top=1, bottom = 0.08, wspace=0, hspace=0)

    f_list = [ '_'.join([os.path.join(output_dir, measure), 'lh', surface, 'lateral.png']),
               '_'.join([os.path.join(output_dir, measure), 'rh', surface, 'lateral.png']),
               '_'.join([os.path.join(output_dir, measure), 'lh', surface, 'medial.png']),
               '_'.join([os.path.join(output_dir, measure), 'rh', surface, 'medial.png']) ]

    # Plot each figure in turn
    for g_loc, f in zip(grid, f_list):
        ax = plt.Subplot(fig, g_loc)
        fig.add_subplot(ax)
        img = mpimg.imread(f)
        # Crop the figures appropriately
        # NOTE: this can change depending on which system you've made the 
        # images on originally - it's a bug that needs to be sorted out!
        if 'lateral' in f:
            img_cropped = img[75:589,55:(-50),:]
        else:
            img_cropped = img[45:600,25:(-25),:]
        ax.imshow(img_cropped, interpolation='none')
        ax.set_axis_off()

    # Add the bottom of one of the images as the color bar
    # at the bottom of the combo figure
    grid_cbar = gridspec.GridSpec(1,1)
    grid_cbar.update(left=0, right=1, top=0.08, bottom=0, wspace=0, hspace=0)
    ax = plt.Subplot(fig, grid_cbar[0])
    fig.add_subplot(ax)
    img = mpimg.imread(f)
    img_cbar = img[600:,:]
    ax.imshow(img_cbar, interpolation='none')
    ax.set_axis_off()
    
    # Save the figure
    filename = os.path.join(output_dir, '{}_{}_combined.png'.format(measure, surface))
    print filename
    fig.savefig(filename, bbox_inches=0, dpi=300)


#=============================================================================
# SET SOME VARIABLES
#=============================================================================
# Read in the arguments from argparse
arguments, parser = setup_argparser()

subject_id = arguments.fsaverageid
subjects_dir = arguments.subjects_dir
roi_data_file = arguments.roi_file
l = arguments.lower
u = arguments.upper
cmap = arguments.cmap
color_file = arguments.color_file
center = arguments.center
surface = arguments.surface
thresh = arguments.thresh

# Define the output directory
output_dir = os.path.join(os.path.dirname(roi_data_file), 'PNGS')
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

# Define the name of the measure you're plotting
measure = os.path.basename(roi_data_file)
measure = os.path.splitext(measure)[0]

# Define the aparc names
# Read in aparc names file
aparc_names_file =  os.path.join(subjects_dir,
                          subject_id, "parcellation",
                          "500.names.txt")
                          
# Read in the names from the aparc names file 
# dropping the first 41
aparc_names = [line.strip() for line in open(aparc_names_file)]
aparc_names = aparc_names[41::]

# Figure out which surfaces you're going to use
if surface == 'both':
    surface_list = [ "inflated", "pial" ]
elif surface == 'inflated':
    surface_list = [ "inflated" ]
elif surface == 'pial':
    surface_list = [ "pial" ]
else:
    print "Do not recognise surface. Check {}".format(surface)
    parser.print_help()
    sys.exit()
    
hemi_list = [ "lh", "rh" ]
views_list = [ 'medial', 'lateral' ]

seg = '500cortConsec'

# Check that the inputs exist:
if not os.path.isfile(roi_data_file):
    print "Roi data file doesn't exist"
    sys.exit()
    
if not os.path.isdir(os.path.join(subjects_dir, subject_id, "surf")):
    print "Fsaverage directory doesn't exist"
    print "Check subjects_dir and subject_id"
    sys.exit()
    
#=============================================================================
# READ IN THE MEASURE DATA
#=============================================================================
# Read in the data
df = pd.read_csv(roi_data_file, index_col=False, header=None)

#-------
# Make custom colorbar
if color_file:
    colors = [line.strip() for line in open(color_file)]
    l = 1
    u = len(colors)
else:
    # Set l and u so that they're the same for both hemispheres
    l, u = calc_range(df[0], l, u, thresh, center)

# Now rearrange the data frame and match it up with 
# the aparc names
df = df.T
df.columns = aparc_names

# Now make your pictures
for hemi, surface in it.product(hemi_list, surface_list):

    prefix = '_'.join([measure, hemi, surface])
    
    # Read in aparc annot file which will be inside
    # the label folder of your fsaverage subject folder
    aparc_file = os.path.join(subjects_dir,
                          subject_id, "label",
                          hemi + ".500.aparc.annot")

    # Use nibabel to merge together the aparc_names and the aparc_file
    labels, ctab, names = nib.freesurfer.read_annot(aparc_file)

    # Create an empty roi_data array
    roi_data = np.ones(len(names))*(thresh-1.0)

    # Loop through the names and if they are in the data frame
    # for this hemisphere then add that value to the roi_data array
    for i, name in enumerate(names):
        roi_name = '{}_{}'.format(hemi, name)

        if roi_name in df.columns:
            roi_data[i] = df[roi_name]
            
    # Make a vector containing the data point at each vertex.
    vtx_data = roi_data[labels]
    
    # Show this data on a brain
    if colors:
        plot_surface(vtx_data, subject_id, hemi,
                     surface, subjects_dir, 
                     output_dir, prefix,
                     l, u, colors,
                     thresh)
		     
    else:
        plot_surface(vtx_data, subject_id, hemi,
                     surface, subjects_dir, 
                     output_dir, prefix,
                     l, u, cmap,
                     thresh)
		     

#============================================================================= 
# COMBINE THE IMAGES
#============================================================================= 
for surface in surface_list:
    combine_pngs(measure, surface, output_dir)