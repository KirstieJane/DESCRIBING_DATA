#!/usr/bin/env python

'''
Combine multiple pngs into one horizontal image

Created on: 29th August 2013
Created by: Kirstie Whitaker
   Contact:  kw401@cam.ac.uk
'''

#==============================================================================
# IMPORT WHAT YOU NEED
import os
import sys
import glob
import numpy as np
import matplotlib.pylab as plt
import matplotlib.image as mpimg
import argparse

#==============================================================================
def setup_argparser():
    '''
    # CODE TO READ ARGUMENTS FROM THE COMMAND LINE AND SET OPTIONS
    # ALSO INCLUDES SOME HELP TEXT
    '''
    
    # Build a basic parser.
    help_text = ('Combine a selection of png images')
    
    sign_off = 'Author: Kirstie Whitaker <kw401@cam.ac.uk>'
    
    parser = argparse.ArgumentParser(description=help_text, epilog=sign_off)
    
    # Now add the arguments
    # Required argument: png_dir
    parser.add_argument(dest='png_dir', 
                            type=str,
                            metavar='png_dir',
                            help='Directory that contains the png files')
    
    # Optional argument: png_file
    parser.add_argument('-f', '--png_file_list',
                            dest='png_file_list', 
                            type=str,
                            metavar='png_file_list',
                            help='File containing a list of png names')

    # Optional argument: transparency
    #       default: False
    parser.add_argument('-tr', '--transparency',
                            dest='transparency',
                            action='store_true',
                            help='Make background transparent. Default is black')
    
    # Optional argument: width_ratio
    #       default: 1.3
    parser.add_argument('-wr', '--width_ratio',
                            dest='width_ratio',
                            type=float,
                            default=1.3,
                            help='Percentage of png overlap')
    
    arguments = parser.parse_args()
    
    return arguments, parser

def plot_bg(png, n, arguments, diff):

    # Read in the example png
    img = mpimg.imread(png)
    
    # Generate a background image that has the same height,
    # as the png but n * the 
    bg = np.ones([img.shape[0], img.shape[1]*n* (1-diff)])
    
    fig_shape = ( 25, (25 * n * (1-diff) * img.shape[1]/img.shape[0]))
    
    # Create a new figure that has the shape described above
    f = plt.figure('Combined_Images',(fig_shape))
    
    # Generate an axis that covers the whole figure
    ax = plt.axes([0, 0, 1, 1], frameon=False)
    f.add_axes(ax)
    
    # Turn off axis labels
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Now cover the axis in black or white
    cmap='gray'
    if arguments.transparency:
        cmap = 'gray_r'

    ax.imshow(bg, cmap=cmap)

    return f

    
def plot_pngs(f, i, png, n, w, d, arguments):
    '''
    This function reads in the counter (i), the png file (png),
    the total number of pngs, and the width and height of the
    figure
    '''
    
    # Load the png file to numpy
    img = mpimg.imread(png)

    png_filename = os.path.split(png)[1]

    # Flip sagittal pictures if they're on the left side
    # (indicated by negative mni values)
    if '_-' in png_filename and png_filename.startswith('s'):
        img = np.fliplr(img)
        
    # Mask the image to exclude 0s
    m_img = np.ma.masked_where(img==0.,img)

    # Calculate the start position along the xaxis
    s = (i * (1-d))/n
    
    # Create your axis
    ax = plt.axes([s, 0, w, 1], frameon=False)
    f.add_axes(ax)
    
    # And then show your image
    image = ax.imshow(m_img, interpolation='none')

    # Add a black line around the edge of the image
    # it makes the brain look nicer :)
    CS = plt.contour(img[:,:,0], [0.0, 1], linewidths=1, colors='k')

    # Write the MNI value on to the slice
    mni = np.float(png[-8:-4])
    
    if png_filename.startswith('s'):
        mni_text = 'X = {:1.0f}'.format(mni)
    
        # Define where the text should sit on the picture
        text_posn_x = 0.75
        text_posn_y = 0.07
        # Flip sagittal slices that are on the left
        if '_-' in png_filename:
            text_posn_x = 0.25

    if png_filename.startswith('a'):
        mni_text = 'Z = {:1.0f}'.format(mni)
    
        # Define where the text should sit on the picture
        text_posn_x = 0.50        
        text_posn_y = 0.00
        
    text_color = 'w'
    if arguments.transparency:
        text_color = 'k'
        
    # Add the mni text to the image
    text = ax.text(text_posn_x, text_posn_y , mni_text,
                        horizontalalignment='center',
                        verticalalignment='bottom',
                        transform=ax.transAxes,
                        color = text_color, fontsize = 130 / n)
    
    # Turn off axis labels
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    
    return f

    
#==============================================================================
# DEFINE OPTIONS
arguments, parser = setup_argparser() # Read arguments from command line

# Set the width ration - 1.3
# I CAN NOT REMEMBER WHAT THIS MEANS BUT IT NEEDS TO GO IN THE ARGUMENTS
#width_ratio = 1.3
width_ratio = arguments.width_ratio/1. # Not necessary if it's stored as float


# -----------------------------------------------------------------------------
# TEMPLATE PNG_LISTS
# -----------------------------------------------------------------------------
# Sagittal
glob_string = ('sagittal*.png')

# create list of pngs
all_sag_pngs = glob.glob(os.path.join(arguments.png_dir,glob_string))

# SYNESTHESIA FIGURE 2
pngs_0 = [ png for png in all_sag_pngs if '0.png' in png ]
syn_sag_pngs = pngs_0[3:6] + pngs_0[(-6):(-3)]

pngs_0_5 = [ png for png in all_sag_pngs if '0.png' in png or '5.png' in png ]

n = len(pngs_0_5)/1.
half = np.floor(n/2)
# Right hemisphere sagittal
right_pngs = pngs_0_5[4:np.int(half)]
# Left hemisphere sagittal
left_pngs = pngs_0_5[np.int(half):(-4)]

whole_pngs = pngs_0_5[2:(-2):2]

# Axial
glob_string = ('axial*png')
all_ax_pngs = glob.glob(os.path.join(arguments.png_dir, glob_string))

pngs_0 = [ png for png in all_ax_pngs if '0.png' in png ]

syn_ax_pngs = pngs_0[4:11]

# Coronal
#glob_string = ('coronal*png')

combo_list = [ whole_pngs, right_pngs, left_pngs, syn_sag_pngs, syn_ax_pngs ]

for l in combo_list:
    l.sort()

# Custom list
if arguments.png_file_list:
    with open(arguments.png_file_list) as f:
        custom_pngs = f.read().splitlines()

    combo_list = combo_list + [custom_pngs]
    
combo_list = [ l for l in combo_list if len(l) > 0 ]

for pngs in combo_list:
    # Calculate the number of pngs you're going to show
    n = len(pngs)/1.
    diff = width_ratio - 1
    d = diff/n
    w = width_ratio/n

    #========

    # I ALSO DON'T KNOW WHAT THIS MEANS
    #backwards=True

    # Name the output file of the form:
    # combined_<sliceorientation>_<lowest_mni>_<highest_mni>.png
    png0_filename = os.path.split(pngs[0])[1]
    png_last_filename = os.path.split(pngs[-1])[1]
    
    png_name = 'combined_{}_{}_to_{}.png'.format(png0_filename.split('_')[0],
                                        png_last_filename[-8:-4],
                                        png0_filename[-8:-4])
                                        

    fig = plot_bg(pngs[0], n, arguments, diff)

    # The various orientations look best displayed with
    # different options

    if png0_filename.split('_')[0].startswith('s'):
        
        # Get MNI values
        mnis = [ np.float(png[-8:-4]) for png in pngs ]
        
        # Find absolute mni values
        mnis_abs = [ np.abs(mni) for mni in mnis ]
        
        # Define sort by absolute mni_values
        sort_ids = np.argsort(mnis_abs)
        
        # Create image list sorted by absolute mni_values
        image_list = np.array(pngs)[sort_ids]
        
        # Reverse the sort_ids for plotting
        sort_ids_rev = sort_ids.max() - sort_ids
        
        # Plot the middle one first
        middle_png = [ png for png in pngs if '_+000.png' in png ]
        
        if middle_png:
            middle_png = middle_png[0]
            middle_id = pngs.index(middle_png)
            fig = plot_pngs(fig, middle_id, middle_png, n, w, d, arguments)
        #else:
        #    middle_png == '0'
        
        # Now plot the rest of them
        # i tells plot_pngs which order to put them in
        for i, png in reversed(zip(sort_ids_rev, image_list)):
            if not png == middle_png:
                fig = plot_pngs(fig, i, png, n, w, d, arguments)

        # Save the figure
        
        fig.savefig(os.path.join(arguments.png_dir, png_name),
                        transparent=True,
                        bbox_inches='tight',
                        edgecolor='none')
        
        #plt.show()
        plt.close()

    if png0_filename.split('_')[0].startswith('a'):
        
        # Get MNI values
        mnis = [ np.float(png[-8:-4]) for png in pngs ]
        
        # Define sort by mni_values
        sort_ids = np.argsort(mnis)
        
        # Create image list sorted by mni_values
        image_list = np.array(pngs)[sort_ids]
        
        # i tells plot_pngs which order to put them in
        for i, png in zip(sort_ids, image_list):
            fig = plot_pngs(fig, i, png, n, w, d, arguments)

        # Add the R and L text indicators to the right and left of the image
        # Generate an axis that covers the whole figure
        ax = plt.axes([0, 0, 1, 1], frameon=False)
        fig.add_axes(ax)
        
        ax = fig.gca()
        
        text_color = 'w'
        if arguments.transparency:
            text_color = 'k'
            
        text = ax.text(0.00, 0.5, 'L',
                            horizontalalignment='left',
                            verticalalignment='center',
                            transform=ax.transAxes,
                            color = text_color, fontsize = 200 / n)
        text = ax.text(1.00, 0.5, 'R',
                            horizontalalignment='right',
                            verticalalignment='center',
                            transform=ax.transAxes,
                            color = text_color, fontsize = 200 / n)
        
        # Save the figure        
        fig.savefig(os.path.join(arguments.png_dir, png_name),
                        transparent=True,
                        bbox_inches='tight',
                        edgecolor='none')
        
        plt.close()
#=============================================================================
# Here's the fun part
