#!/usr/bin/env python

'''
Need a doc string!
'''

import numpy as np
import matplotlib.pylab as plt
import itertools as it
from matplotlib.ticker import MaxNLocator, FormatStrFormatter, FixedLocator
import collections
import sys
import string
import platform
import os

if platform.system() == 'Windows':
    if os.path.isdir('C:\\Users\\Kirstie'):
        sys.path.insert(0, 'C:\\Users\\Kirstie\\Dropbox\\GitHub\\GENERAL_CODE\\')
        sys.path.insert(0, 'C:\\Users\\Kirstie\\Dropbox\\GitHub\\DOWNLOADED_CODE\\')
    elif os.path.isdir('C:\\Users\\steve'):
        sys.path.insert(0, 'C:\\Users\\steve\\Dropbox\\GitHub\\GENERAL_CODE\\')
        sys.path.insert(0, 'C:\\Users\\steve\\Dropbox\\GitHub\\DOWNLOADED_CODE\\')
    
elif platform.system() == 'Linux':
    sys.path.insert(0, '/home/kw401/CAMBRIDGE_SCRIPTS/GENERAL_SCRIPTS/')
    sys.path.insert(0, '/home/kw401/CAMBRIDGE_SCRIPTS/DOWNLOADED_CODE/')

else:
    print 'Can\'t find MyCoolFunctions or ols scripts.'
    print 'Check the names of the directories!'

# Import your personal scripts
import MyCoolFunctions as mcf
# Import downloaded python scripts
# I don't understand why the import doesn't work :(
#import ols
execfile('C:\\Users\\steve\\Dropbox\\GitHub\\DOWNLOADED_CODE\\ols.0.2.py')

# Define group_dictonary
group_dict = dict()
group_dict['Depressed_0'] = 'Con'
group_dict['Depressed_1'] = 'Dep'
group_dict['Depressed_2'] = 'All'
group_dict['Meds_0'] = 'NoMed'
group_dict['Meds_1'] = 'Med'
group_dict['Meds_2'] = 'IgMed'
group_dict['UsableCort_0'] = 'NoCort'
group_dict['UsableCort_1'] = 'Cort'
group_dict['UsableCort_2'] = 'IgCort'

def usage():
    print 'KIRSTIE - make a usage function!!!'
#------------------------------------------------------------------------------

def create_names(input_filename, group_dict):
    '''
    This script is designed to work beautifully with another script: Randomise_setup.py
    The file names that that script creates have a few words in them that are
    not data labels. This function makes sense of those file names :)
    '''
    # Stripe the file ending, and then split on '_'
    file_name = input_filename.rsplit('/')[-1].rsplit('.')[0]
    names = file_name.split('_')
    
    for i, name in enumerate(names):
        # If you have a TTest style name:
        if name == 'TTest':
            # First remove the word TTest
            names.pop(i)
            # The next string is what you're performing the TTest on
            # eg: DepCon
            comparison = names[i]
            names.pop(i)
            # Loop through the group_dict.value()
            for group in group_dict.values():
                # If there is a value (eg: Dep) in the comparison string
                # (eg: DepCon) then insert that name into the names list
                if group in comparison:
                    names.insert(i, group)
                # These names are actually the wrong way round though
                # (doh - there is a reason but blah)
                # so we have to flip them around!
                name_group = names.pop(i)
                names.insert(i-1,name_group)
                
                # You don't have to, but you may have additional covariates
                # after the TTest
                if len(names) > 2:
                    # The next word will be 'Corr' or 'Int'
                    # remove that
                    test = names.pop(i+2)
                    covar = names[i+2]
                    if test == 'Int':
                        # If you have an interaction then the next word
                        # is a measure that you're testing an interaction
                        # with group on. You need to remove that and replace
                        # it with two different column names
                        names.pop(i+2)
                        names.insert(i+2,names[i]+ '_' + covar)
                        names.insert(i+3,names[i+1]+ '_' + covar)
    
    ignore_list = [ 'Corr', 'Covar' ]
    names = [ name for name in names if not name in ignore_list ]
    names = [ name for name in names if not name.startswith('Excl') ]
    
    return names
#------------------------------------------------------------------------------

def load_data(input_filename, group_dict):
    '''
    This function reads in your data as a numpy array.
    It can cope with either an FSL-style .mat file, or just a text file
    with columns of numbers (either space, tab or comma delimited)
    '''
    # Before we read in the data, test to see if the word "\Matrix" appears
    # If it does then we'll skip all lines until the one below that word
    skip=0
    for i, line in enumerate(open(input_filename)):
        if ' ' in line:
            delimiter=' '
        if '\t' in line:
            delimiter='\t'
        if ',' in line:
            delimiter=','
        if  '/Matrix' in line:
            skip = i
            break

    data = np.loadtxt(input_filename, skiprows=skip+1, delimiter=delimiter)

    names = create_names(input_filename, group_dict)

    if not len(names)==data.shape[1]:
        names =  [ 'data_' + letter for letter in string.ascii_uppercase[:data.shape[1]] ]
    
    return data, names
#------------------------------------------------------------------------------

def def_x_y_rem(data, x, y):
    xdata = data[:,x]
    ydata = data[:,y]
    rem_indices = [ i for i in range(data.shape[1]) if not ( i == x or i == y ) ]
    remdata = data[:,rem_indices] if rem_indices else False
    return xdata, ydata, remdata
#------------------------------------------------------------------------------

def KW_set_axis_range(unique):
    diff = unique[1] - unique[0]
    locations = np.linspace(unique[0] - diff/2, unique[1] + diff/2, 5)
    majorlocator = FixedLocator(unique)
    majorformatter = FormatStrFormatter('%.2f')
    return locations, majorlocator, majorformatter
#------------------------------------------------------------------------------

def adjust_sig_figs(data):
    counter=0
    while ( np.abs(data.max()) > 1000 ):
        data /= 1000
        counter += 1
    if not np.abs(data.min()) == 0 and np.all(data[data > 0.000000000001]):
        while ( np.abs(data[data!=0].min()) < 1 ):
            data *= 1000
            counter -= 1
    return data, counter
#------------------------------------------------------------------------------

def run_pairwise_correlations(xdata, ydata):
    if not np.all(xdata == ydata):
        # Run a pairwise regression
        ols_pair = ols(ydata, xdata, x_varnm=['x'])
        res = ols_pair.e
        est_ydata = ydata - res
        r2 = ols_pair.R2
        p = ols_pair.p[1]
    else:
        est_ydata = ydata
        r2 = 1.
        p = 0.
    return est_ydata, r2, p
#------------------------------------------------------------------------------

def run_partial_correlations(xdata, ydata, remdata):
    # Now create the added variable plot
    # Correlate x and y separately against
    # all the other data excluding the other
    # This can only be done if you have more than 2
    # columns of data!
    try:
        ols_partial_x = ols(xdata, remdata)
        partial_res_x = ols_partial_x.e
    except:
        partial_res_x = np.zeros_like(xdata)
    
    try:
        ols_partial_y = ols(ydata, remdata)
        partial_res_y = ols_partial_y.e
    except:
        partial_res_y = np.zeros_like(ydata)
        
    try:
        ols_partial_xy = ols(partial_res_y, partial_res_x, x_varnm=['x'])
        partial_res_res = ols_partial_xy.e
        est_partial_res_y = partial_res_y - partial_res_res
        r2 = ols_partial_xy.R2
        p = ols_partial_xy.p[1]
    except:
        est_partial_res_y = np.zeros_like(ydata)
        r2 = 1.
        p = 0.
    
    return partial_res_x, partial_res_y, est_partial_res_y, r2, p
#------------------------------------------------------------------------------

def setup_axes(ax, xdata, ydata):
    # X axis:
    # Find the number of unique data points
    xunique = np.unique(xdata)
    # If there are only two unique points then we're going to set the
    # axis ticks at just 2 points
    if xunique.shape[0] == 2:
        xlocations, xmajorlocator, xmajorformatter = KW_set_axis_range(xunique)
        ax.set_xlim(xlocations[0], xlocations[-1])
        ax.xaxis.set_major_formatter(xmajorformatter)
    else:
        xmajorlocator = MaxNLocator(6, prune='both')
    
    ax.xaxis.set_major_locator(xmajorlocator)
    
    # Y axis:
    yunique = np.unique(ydata)
    if yunique.shape[0] == 2:
        ylocations, ymajorlocator, ymajorformatter = KW_set_axis_range(yunique)
        ax.set_ylim(ylocations[0], ylocations[-1])
        ax.yaxis.set_major_formatter(ymajorformatter)
    else:
        ydata, ycounter = adjust_sig_figs(ydata)
        ymajorlocator = MaxNLocator(6, prune='both')
    
    ax.yaxis.set_major_locator(ymajorlocator)
    
    return ax
#------------------------------------------------------------------------------

def calculate_sizes(ax, xdata, ydata, est_ydata):
    # Figure out how big each dot should be
    # Determine the sizes of each dot
    
    # Round the data to 3 sf so that if there are near
    # duplicates then they'll be plotted together in one 
    # big circle
    xdata_round = mcf.KW_round(xdata,3)
    ydata_round = mcf.KW_round(ydata,3)
    est_ydata_round = mcf.KW_round(est_ydata,3)
    
    combo_data = np.vstack([xdata_round, ydata_round]).T
    
    counter = collections.Counter(tuple(p) for p in combo_data)
    
    plot_data = np.array(counter.keys())
    
    sizes = np.array(counter.values())
    sizes = sizes * 20
    sizes = sizes[plot_data[:,0].argsort()]
    
    plot_data = plot_data[plot_data[:,0].argsort()]

    identical = False
    
    if not np.any(ydata_round - est_ydata_round):
        identical = True
    
    return plot_data, sizes, identical
#------------------------------------------------------------------------------

def create_plot(png_name, data, names):
    print png_name

    # Set your regline and partial options
    regline = False if 'noline' in png_name else True
    partial = False if 'pairwise' in png_name else True

    # Define your figure and axes
    f, axarr = plt.subplots(data.shape[1], data.shape[1],
                            figsize=(16, 12), dpi=80,
                            facecolor='w', edgecolor='k',
                            sharex='col', sharey='row')

    # Define the x, y coordinates of the subplots you're going to show
    # (n * n with diagonal showing but not those below it)
    full_coord_list = [ (x, y) for x in range(data.shape[1]) for y in range(data.shape[1]) ]
    show_coord_list = [ (x, y) for x in range(data.shape[1]-1) for y in range(data.shape[1]-1) if x > y ]
    
    # Loop through the axes:
    for x,y in full_coord_list:
        # We want to flip the xaxis around so it counts from 
        # right to left (to aviod weird white space in the figure)
        # so we'll index it as (x*-1)+data.shape[1]-1
        # (eg: for a 5x5 array, it will loop: 4,3,2,1 then 0 )
        ax = axarr[y,(x*-1)+data.shape[1]-1]
        if x >= y:
            
            # First, define the x and y data:
            xdata, ydata, remdata = def_x_y_rem(data, x, y)

            # Adjust the significant figures as needed
            #xdata, xcounter = adjust_sig_figs(xdata)
            #ydata, ycounter = adjust_sig_figs(ydata)

            if not partial:
            # Run the pairwise correlations
                est_ydata, r2, p = run_pairwise_correlations(xdata, ydata)

            # Run the partial correlations if the remdata isn't empty
            elif remdata.dtype == float:
                xdata, ydata, est_ydata, r2, p = run_partial_correlations(xdata, ydata, remdata)

            else:
                print 'Can\'t calculate partial regression plot, too few variables'
                return
            
            # Set up the axes
            ax = setup_axes(ax, xdata, ydata)

            # Calculate the sizes and plot data for each of the points
            plot_data, sizes, identical = calculate_sizes(ax, xdata, ydata, est_ydata)
            
            # Plot the data
            ax.scatter(plot_data[:,0], plot_data[:,1], s=sizes)
            
            # Add the regline if you're supposed to
            # and if the data isn't exactly the same
            if regline and not identical:
                ax.plot(xdata, est_ydata, color = 'r')
            
                # Also add the r2 and p values
                ax.text(0.02, 0.98,'$R^2$: {:2.2f}\n$p$: {:3.3f}'.format(r2, p),
                            ha='left', va='top',
                            transform=ax.transAxes)

            # Label the x and y axes
            ax.set_xlabel(names[x])
            ax.set_ylabel(names[y])

            #if xcounter:
                #print xcounter
                #ax.annotate(0.9, 0.1, '$x10^{}$'.format(xcounter),
                            #ha='center', va='center',
                            #transform = ax.transAxes)
        else:
            ax.axis('off')
    
    # Set the gap between the subplots to zero
    f.subplots_adjust(hspace=0)
    f.subplots_adjust(wspace=0)
    
    for ax in axarr[:, :].flat:
        for label in ax.get_xticklabels():
            label.set_visible(True)

    # Hide all xlabels except those on the reverse diagonal
    mask = np.fliplr(np.eye(data.shape[1]))==0
    plt.setp([a.get_xticklabels() for a in axarr[mask].reshape(-1)], visible=False)
    xlabels = [a.set_xlabel(' ') for a in axarr[mask].reshape(-1)]

    # Hide all ylabels except those on the left
    plt.setp([a.get_yticklabels() for a in axarr[:,1:].reshape(-1)], visible=False)
    ylabels = [a.set_ylabel(' ') for a in axarr[:,1:].reshape(-1)]
    
    plt.show()
#==============================================================================
# Define some variables
try:
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
except IndexError:
    print 'EXITING - Check your input arguments'
    usage()
    sys.exit()
#==============================================================================
# Run the main code:

# Load in the data
data, names = load_data(input_filename, group_dict)

# Now make your various figures
png_names = [ 'pairwise_noline', 'pairwise_line', 'partial_noline', 'partial_line' ]
#png_names = [ 'pairwise_line' ]
for png_name in png_names:
    create_plot(png_name, data, names)


for i in range(0, data.shape[1]):
    not_i = range(0,data.shape[1])
    not_i.pop(i)
    x_names = list(names)
    x_names.pop(i)
    overall_ols = ols(data[:,i], data[:,not_i], y_varnm=names[i], x_varnm=x_names)
    print overall_ols.summary()

# The end