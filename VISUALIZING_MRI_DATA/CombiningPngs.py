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

#==============================================================================
def plot_bg(png, n):

    img = mpimg.imread(png)
    
    bg = np.ones([img.shape[1], img.shape[0]*n])
    
    fig_shape = ( 25, bg.shape[1] / img.shape[1] * 25 )
    f = plt.figure('Combined_Images',(fig_shape))
    
    ax = plt.axes([0, 0, 1, 1], frameon=False)
    
    ax.imshow(bg, cmap='gray')
    
    # Turn off axis labels
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    return f

    
def plot_pngs(i, png, n, w, d):
    
    img = mpimg.imread(png)

    if '_-' in png and png.startswith('s'):
        img = np.fliplr(img)
    m_img = np.ma.masked_where(img==0.,img)

    s = (i * (1-d))/n
    
    # Create your axis
    ax = plt.axes([s, 0, w, 1], frameon=False)
    
    # And then show your image
    
    image = ax.imshow(m_img, interpolation='none')

    # Add a black line around the edge of the image
    # it makes the brain look nicer :)
    CS = plt.contour(img[:,:,0], [0.0, 1], linewidths=1, colors='k')

    # Write a text
    mni = np.float(png[-8:-4])
    mni_text = 'X = {:3.0f}'.format(mni)
    
    text_posn_x = 0.75
    if '_-' in png and png.startswith('s'):
        text_posn_x = 0.25
        
    text = ax.text(text_posn_x, 0.1 , mni_text,
                        horizontalalignment='center',
                        verticalalignment='bottom',
                        transform=ax.transAxes,
                        color = 'w')
    
    # Turn off axis labels
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    
#==============================================================================
# DEFINE OPTIONS

glob_string = "s*.png"
width_ratio = 1.3
backwards=True
width_ratio = width_ratio/1.

output_dir = os.getcwd()

pngs = glob.glob(glob_string)
pngs.sort()

pngs = [ png for png in pngs if '0.png' in png or '5.png' in png ]


n = len(pngs)/1.

half = np.floor(n/2)
#pngs = pngs[4:np.int(half)]
pngs = pngs[2:(-2):2]

png_name = 'combined_{}_{}_to_{}.png'.format(pngs[0].split('_')[0],
                                    pngs[-1][-8:-4],
                                    pngs[0][-8:-4])

n = len(pngs)/1.
diff = width_ratio - 1
d = diff/n
w = width_ratio/n

fig = plot_bg(pngs[0], n)

# The various orientations look best displayed with
# different options

if glob_string.startswith('s'):
    
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
    
    print middle_png
    
    if middle_png:
        middle_png = middle_png[0]
        middle_id = pngs.index(middle_png)
        plot_pngs(middle_id, middle_png, n, w, d)
    else:
        middle_png == '0'
    
    # Remove middle_png from the list - you already have that one
    #image_list.remove(middle_png[0])
    
    for i, png in reversed(zip(sort_ids_rev, image_list)):
        print i, png
        if not png == middle_png:
            plot_pngs(i, png, n, w, d)

    # Save the figure
    plt.savefig(os.path.join(output_dir, png_name),
                    transparent=True,
                    bbox_inches='tight',
                    edgecolor='none')
    
    plt.close()

# END