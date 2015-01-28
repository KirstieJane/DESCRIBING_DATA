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
    min_value = np.min(np.concatenate(values_list))
    
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
    
    # And now turn off the major ticks on the y-axis
    for t in ax.yaxis.get_major_ticks(): 
        t.tick1On = False 
        t.tick2On = False

    return ax

#=============================================================================
def create_violin_plots(df_list, measures_list, measures_names, height, group_names, color='blue', ttest=False, layout='one_row', paired=False, given_ymin=False, given_ymax=False):
    
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
            ax = add_ttest(ax, df_list, measure, paired=paired)

        # Set the y axis limits if given
        ymin, ymax = plt.ylim()
        if given_ymin and given_ymax:
            plt.ylim(given_ymin, given_ymax)
        if given_ymin and not given_ymax:
            plt.ylim(given_ymin, ymax)
        if not given_ymin and given_ymax:
            plt.ylim(ymin, given_ymax)

    # Make sure the layout looks good :)        
    fig.tight_layout()
    
    return fig


#=============================================================================
def calc_ttest_dict(a, b, paired=False):
    '''
    Calculate the comparison between the two sets of data
    
    Importantly, although the stars will be the same, this code
    accurately applies either a Student's t, Welch's t, or Mann Whitney U
    test
    '''
    # Import what you need
    import numpy as np
    from scipy.stats import ttest_ind, ttest_rel, bartlett, mannwhitneyu, normaltest, wilcoxon
    
    stats_dict = {}
    
    # Mask out the not a numbers
    a = [ x for x in a if not np.isnan(x) ]
    b = [ x for x in b if not np.isnan(x) ]

    # Save number of people in each group
    stats_dict['n'] = (len(a), len(b))
    
    # Conduct test for equal variance
    stats_dict['eqvar'] = bartlett(a, b)
    
    # Conduct test for normality
    stats_dict['normal'] = normaltest(np.hstack([a, b]))
    
    # When you test for equal means (ttest) you have different options
    # depending on if you have equal variances or not. You can also
    # run the non-parametric Mann Whitney U test
    # Alternatively these data may be paired so there's also the
    # paired t-test and the Wilcoxon signed rank test
    
    # All five will be entered in the stats_dict
    
    # Conduct Welch's t-test (unequal variances)
    stats_dict['ttest_uneqvar'] = ttest_ind(a, b, equal_var = False)

    # Conduct standard student's t-test (equal variances)
    stats_dict['ttest_eqvar'] = ttest_ind(a, b, equal_var = True)

    # Conduct mann whitney U test (non-parametric test of medians)
    stats_dict['mannwhitneyu'] = mannwhitneyu(a, b)
    
    if paired:
        # Conduct the paired student's t-test
        stats_dict['ttest_paired'] = ttest_rel(a, b)
    
        # Conduct Wilcoxon signed rank test (non-parametric *paired* test of medians)
        stats_dict['wilcoxon'] = wilcoxon(a, b)

    # Save in the stats dict the various other measures you might
    # want to report
    stats_dict['medians'] = [np.percentile(a, 50), np.percentile(b, 50)]
    stats_dict['percentile25'] = [np.percentile(a, 25), np.percentile(b, 25)]
    stats_dict['percentile75'] = [np.percentile(a, 75), np.percentile(b, 75)]
    stats_dict['means'] = [np.mean(a), np.mean(b)]
    stats_dict['stds'] = [np.std(a), np.std(b)]
    stats_dict['dfs'] = [(np.float(stats_dict['n'][0])-1), (np.float(stats_dict['n'][1])-1)]
    stats_dict['pooled_std'] = np.sqrt( (np.float(stats_dict['dfs'][0])*(np.float(stats_dict['stds'][0])**2)
                                     + np.float(stats_dict['dfs'][1])*(np.float(stats_dict['stds'][0])**2))
                                     / (np.float(stats_dict['dfs'][0]) + np.float(stats_dict['dfs'][1])))
    
    if paired:
        stats_dict['mean_difference'] = np.mean(np.array(b)-np.array(a))
        stats_dict['std_difference'] = np.std(np.array(b)-np.array(a))
        stats_dict['median_difference'] = np.percentile(np.array(b)-np.array(a), 50) 
        stats_dict['percentile25_difference'] = np.percentile(np.array(b)-np.array(a), 25) 
        stats_dict['percentile75_difference'] = np.percentile(np.array(b)-np.array(a), 75)
        stats_dict['cohens_d'] = np.float(stats_dict['mean_difference']) / np.float(stats_dict['pooled_std'])
        stats_dict['cohens_d_paired'] = np.float(stats_dict['mean_difference']) / np.float(stats_dict['std_difference'])

    return stats_dict

#=============================================================================
def report_stats_dict(stats_dict, paired=False):
    import numpy as np
    
    if paired:
        if stats_dict['normal'][1] < 0.05:
            print "Not normally distributed data, testing medians"
            print "    Medians: {:2.4f}, {:2.4f}".format(np.float(stats_dict['medians'][0]),
                                                            np.float(stats_dict['medians'][1]))
            print "    IQRs: {:2.4f} to {:2.4f}, {:2.4f} to {:2.4f}".format(np.float(stats_dict['percentile25'][0]),
                                                                                np.float(stats_dict['percentile75'][0]),
                                                                                np.float(stats_dict['percentile25'][1]),
                                                                                np.float(stats_dict['percentile75'][1]))
            print "    Median difference: {:2.4f}".format(np.float(stats_dict['median_difference']))
            print "    IQR difference: {:2.4f} to {:2.4f}".format(np.float(stats_dict['percentile25_difference']),
                                                                                np.float(stats_dict['percentile75_difference']))
            
            print "    Wilcoxon W: {:2.4f}, p = {:2.4f}".format(np.float(stats_dict['wilcoxon'][0]),
                                                                    np.float(stats_dict['wilcoxon'][1]))
                                                                    
        else:
            print "Normally distributed and groups have equal variance"
            print "    Means: {:2.4f}, {:2.4f}".format(np.float(stats_dict['means'][0]),
                                                            np.float(stats_dict['means'][1]))
            print "    St devs: {:2.4f}, {:2.4f}".format(np.float(stats_dict['stds'][0]),
                                                            np.float(stats_dict['stds'][1]))
            print "    Mean difference: {:2.4f}".format(np.float(stats_dict['mean_difference']))
            print "    St dev difference: {:2.4f}".format(np.float(stats_dict['std_difference']))
            print "    Paired student's t : {:2.4f}, p = {:2.4f}".format(np.float(stats_dict['ttest_paired'][0]),
                                                                    np.float(stats_dict['ttest_paired'][1]))
            print "    Cohen's d: {:2.4f}".format(np.float(stats_dict['cohens_d']))

    else:
    
        if stats_dict['normal'][1] < 0.05:
            print "Not normally distributed data, testing medians"
            print "    Medians: {:2.4f}, {:2.4f}".format(np.float(stats_dict['medians'][0]),
                                                            np.float(stats_dict['medians'][1]))
            print "    IQRs: {:2.4f} to {:2.4f}, {:2.4f} to {:2.4f}".format(np.float(stats_dict['percentile25'][0]),
                                                                                np.float(stats_dict['percentile75'][0]),
                                                                                np.float(stats_dict['percentile25'][1]),
                                                                                np.float(stats_dict['percentile75'][1]))
            print "    Mann-Whitney U: {:2.4f}, p = {:2.4f}".format(np.float(stats_dict['mannwhitneyu'][0]),
                                                                    np.float(stats_dict['mannwhitneyu'][1]))
                                                                

        elif stats_dict['eqvar'][1] < 0.05:
            print "Normally distributed but groups don't have equal varience"
            print "    Means: {:2.4f}, {:2.4f}".format(np.float(stats_dict['means'][0]),
                                                            np.float(stats_dict['means'][1]))
            print "    St devs: {:2.4f}, {:2.4f}".format(np.float(stats_dict['stds'][0]),
                                                            np.float(stats_dict['stds'][1]))

            print "    Welch's t: {:2.4f}, p = {:2.4f}".format(np.float(stats_dict['ttest_uneqvar'][0]),
                                                                    np.float(stats_dict['ttest_uneqvar'][1]))
            print "    Cohen's d: {:2.4f}".format(np.float(stats_dict['cohens_d']))
                                                                    
        else:
            print "Normally distributed and groups have equal varience"
            print "    Means: {:2.4f}, {:2.4f}".format(np.float(stats_dict['means'][0]),
                                                            np.float(stats_dict['means'][1]))
            print "    St devs: {:2.4f}, {:2.4f}".format(np.float(stats_dict['stds'][0]),
                                                            np.float(stats_dict['stds'][1]))
            print "    Student's t : {:2.4f}, p = {:2.4f}".format(np.float(stats_dict['ttest_eqvar'][0]),
                                                                    np.float(stats_dict['ttest_eqvar'][1]))
            print "    Cohen's d: {:2.4f}".format(np.float(stats_dict['cohens_d']))


#=============================================================================
def figure_out_test_stat(stats_dict, paired=False):
    '''
    A snazzy little function to figure out from a stats_dict
    which is the right p value to use for the violin plot
    '''
    if paired:
        if stats_dict['normal'][1] > 0.05:
            test_p = stats_dict['ttest_paired'][1]
            test_name = "Paired t-test"
        else:
            test_p = stats_dict['wilcoxon'][1]
            test_name = "Wilcoxon T"
    
    else:
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
def add_ttest(ax, df_list, measure, paired=False):
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
        stats_dict = calc_ttest_dict(df_list[a][measure].values[:], df_list[b][measure].values[:], paired=paired)
        p, test_name = figure_out_test_stat(stats_dict, paired=paired)
                        
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
    
        fontsizes = [ 15, 15, 15, 15, 15, 15, 15, 15 ] # Marker sizes
         
         
    if layout == 'just_one':
        # Generate a figure
        fig = plt.figure(figsize = (height*1.5, height))

        # Add just one subplot
        ax1 = plt.axes()
        
        ax_list = [ ax1 ]
        
        fontsizes = [ 15 ]
            
    return fig, ax_list, fontsizes