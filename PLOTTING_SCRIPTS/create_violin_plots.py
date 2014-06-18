#!/usr/bin/env python

#=============================================================================
def violin_plot(ax, values_list, measure_name, group_names, fontsize, color='blue',  ttest=False):
    '''
    This is a little wrapper around the statsmodels violinplot code
    so that it looks nice :)    
    '''    
    
    # IMPORTS
    import matplotlib.pylab as plt
    import statsmodels.api as sm
    import numpy as np
    
    # Make your violin plot from the values_list
    # Don't show the box plot because it looks a mess to be honest
    # we're going to overlay a boxplot on top afterwards
    plt.sca(ax)
    
    # Adjust the font size
    font = { 'size'   : fontsize}
    plt.rc('font', **font)


    max_value = np.max(np.concatenate(values_list))
    
    vp = sm.graphics.violinplot(values_list,
                            ax = ax,
                            labels = group_names,
                            show_boxplot=False,
                            plot_opts = { 'violin_fc':color ,
                                          'cutoff': True,
                                          'cutoff_val': max_value,
                                          'cutoff_type': 'abs'})
    
    
    # Now plot the boxplot on top
    bp = plt.boxplot(values_list, sym='x')
    
    for key in bp.keys():
        plt.setp(bp[key], color='black', lw=fontsize/10)
        
    # Adjust the power limits so that you use scientific notation on the y axis
    plt.ticklabel_format(style='sci', axis='y')
    ax.yaxis.major.formatter.set_powerlimits((-3,3))
    plt.tick_params(axis='both', which='major', labelsize=fontsize)

    # Add the y label
    plt.ylabel(measure_name, fontsize=fontsize)
    
    # And now turn off the major ticks on the y-axix
    for t in ax.yaxis.get_major_ticks(): 
        t.tick1On = False 
        t.tick2On = False

    # Set the y axis limits and calculate the difference
    ymin, ymax = plt.ylim()

    return ax

#=============================================================================
def create_violin_plots(df_list, measures_list, measures_names, height, group_names, color='blue', ttest=False, layout='one_row'):
    
    # IMPORTS
    import matplotlib.pylab as plt
    import numpy as np

    print layout
    # Create a figure
    # and add the appropriate subplots
    fig, ax_list, fontsizes = get_fig(height, len(measures_list), layout=layout)
        
    # Loop through the continuous measures
    for i, (measure, name, fontsize) in enumerate(zip(measures_list, measures_names, fontsizes  )):
        print i, measure, name, fontsize
                        
        ax = ax_list[i]
        
        values_list = []
        for df in df_list:
            v = [ x for x in df[measure] if not np.isnan(x) ]
            values_list.append(np.array(v))
        
        ax = violin_plot(ax, values_list, name, group_names, fontsize, color=color,  ttest=ttest)

        # Finally, if you want to add the t-test statistic
        # then go ahead and do so!
        if ttest:
            ax = add_ttest(ax, df_list, measure)

    # Make sure the layout looks good :)        
    fig.tight_layout()
    
    return fig


#=============================================================================
def calc_ttest_dict(a, b):
    '''
    Calculate the comparison between the two sets of data
    
    Importantly, although the stars will be the same, this code
    accurately applies either a Student's t, Welch's t, or Mann Whitney U
    test
    '''
    # Import what you need
    import numpy as np
    from scipy.stats import ttest_ind, bartlett, mannwhitneyu, normaltest
    
    stats_dict = {}
    
    # Mask out the not a numbers
    a = [ x for x in a if not np.isnan(x) ]
    b = [ x for x in b if not np.isnan(x) ]

    # Conduct test for equal variance
    stats_dict['eqvar'] = bartlett(a, b)
    
    # Conduct test for normality
    stats_dict['normal'] = normaltest(np.hstack([a, b]))
    
    # When you test for equal means (ttest) you have different options
    # depending on if you have equal variances or not. You can also
    # run the non-parametric Mann Whitney U test
    
    # All three will be entered in the stats_dict
    
    # Conduct Welch's t-test (unequal variances)
    stats_dict['ttest_uneqvar'] = ttest_ind(a, b, equal_var = False)

    # Conduct standard student's t-test (equal variances)
    stats_dict['ttest_eqvar'] = ttest_ind(a, b, equal_var = True)

    # Conduct mann whitney U test (non-parametric test of medians)
    stats_dict['mannwhitneyu'] = mannwhitneyu(a, b)
    
    return stats_dict
    
    
#=============================================================================
def figure_out_test_stat(stats_dict):
    '''
    A snazzy little function to figure out from a stats_dict
    which is the right p value to use for the violin plot
    '''
    if stats_dict['normal'][1] > 0.05:
        if stats_dict['eqvar'][1] > 0.05:
            test_p = stats_dict['ttest_eqvar'][1]
            test_name = "Student's t"
        else:
            test_p = stats_dict['ttest_uneqvar'][1]
            test_name = "Welch's t"
    else:
        test_p = stats_dict['mannwhitneyu'][1]*2 # Multiply by 2 to get 2 tailed test
        test_name = "Mann Whitney U"

    return test_p, test_name


#=============================================================================
def add_ttest(ax, df_list, measure):
    '''
    This section of code plots a line between two of the measures
    and also assigns ns, *, ** or *** according to the two tailed
    t-test for that pair of measures.    
    '''
    
    # IMPORTS
    import itertools as it
    import matplotlib.pylab as plt

    # First, you need to know how many tests you're going to conduct
    # You can probably calcuate this but we're actually just going to
    # loop through and get a little counter going
    n_combo=0
            
    for combo in it.combinations(range(len(df_list)), 2):
        n_combo+=1
        
    # Set the axis to be your current working axis
    plt.sca(ax)
    
    # Get the y axis limits and calculate the difference
    ymin, ymax = plt.ylim()
    yrange = ymax - ymin
            
    # Now we're going to calculate where all the various lines are going
    # to go for these tests:
    step_up = yrange * 0.1
            
    # Make the y axis run from just below the ymin, and increase
    # the max to one step above (ymax + step_up * n_combos)
    plt.ylim(ymin - 0.1*yrange, ymax + (step_up * (n_combo + 1)))

    # So, now we know where these lines are going to be placed
    # start a counter for the combinations
    counter=0
            
    # Loop through the combinations again 
    # but this time calculate the t-test statistic
    for a, b in it.combinations(range(len(df_list)), 2):
        
        # Increase the counter so you know where you're at
        # (Note - doing this right away means you're counting
        # from 1 rather than 0)
        counter+=1
                
        # Calculate the test statistics and choose the correct one
        stats_dict = calc_ttest_dict(df_list[a][measure].values[:], df_list[b][measure].values[:])
        p, test_name = figure_out_test_stat(stats_dict)
                        
        # Figure out the text you're going to put on the plot
        star = 'ns'
        if 0.01 < p < 0.05:
            star = '*'
        elif 0.001 <= p < 0.01:
            star = '**'
        elif p < 0.001:
            star = '***'
        
        # We're going to plot the line that shows which test you're conducting
        # at increments of the step up measure
        y = (counter - 0.5) * step_up + ymax

        # The drop (the amount that the line goes down above the two measures
        # you care about) is going to be 2% of the range of the data
        drop = yrange/ 50

        plt.plot([a + 1.0, b + 1.0], [y, y], color='k')
        plt.plot([a + 1.0, a + 1.0], [y, y-drop], color='k')
        plt.plot([b + 1.0, b + 1.0], [y, y-drop], color='k')
        text = ax.text( (a + b) / 2.0 + 1.0, y, star,
            horizontalalignment='center',
            verticalalignment='bottom',
            color = 'k')
            
        print a, b, test_name, p
        
    return ax
        
#======================================================================================
def get_fig(height, n, layout='one_large_three_small'):
    
    import matplotlib.pylab as plt
    
    if layout == 'one_large_three_small':
    
        # Generate a figure
        fig = plt.figure(figsize = (4*height, 3*height))
        
        # Create the four subplots
        ax1 = plt.subplot2grid((3,4), (0,0), colspan=3, rowspan=3)
        ax2 = plt.subplot2grid((3,4), (0,3))
        ax3 = plt.subplot2grid((3,4), (1,3))
        ax4 = plt.subplot2grid((3,4), (2,3))

        # Create your axes list
        ax_list = [ ax1, ax2, ax3, ax4 ]

        fontsizes = [ 10*height, 5*height, 5*height, 5*height ] # Marker sizes
    

    if layout == 'one_row':
        # Generate a figure
        fig = plt.figure(figsize = (n*height, height))
        
        ax_list = []
        for i in range(n):
            ax = plt.subplot2grid((1,n), (0,i))
            ax_list.append(ax)
    
        fontsizes = [ 15, 15, 15, 15 ] # Marker sizes
         
         
    if layout == 'just_one':
        # Generate a figure
        fig = plt.figure(figsize = (height*1.5, height))

        # Add just one subplot
        ax1 = plt.axes()
        
        ax_list = [ ax1 ]
        
        fontsizes = [ 15 ]
            
    return fig, ax_list, fontsizes