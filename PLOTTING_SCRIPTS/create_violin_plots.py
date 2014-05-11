#!/usr/bin/env python

def create_violin_plots(df_list, measures_list, measures_names, height, group_names, ttest=False):
    import matplotlib.pylab as plt
    import numpy as np
    import statsmodels.api as sm
    from scipy import stats
    from matplotlib.ticker import MaxNLocator
    import itertools as it

    
    fig = plt.figure(figsize=(height*len(measures_list), height))
    
    font = { 'size'   : 22 * height/10}

    plt.rc('font', **font)
    
    # Loop through the continous measures
    for i, measure in enumerate(measures_list):
        ax = fig.add_subplot(1,len(measures_list), i+1)
        
        values = []
        for df in df_list:
            v = [ x for x in df[measure] if not np.isnan(x) ]
            values.append(v)
        
        vp = sm.graphics.violinplot(values,
                                ax = ax,
                                labels = group_names,
                                show_boxplot=False,
                                plot_opts = { 'violin_fc':plt.cm.Paired(10.0/13.0) ,
                                              'cutoff': True,
                                              'cutoff_val': max(values),
                                              'cutoff_type': 'abs'})
        
        bp = plt.boxplot(values, sym='x')
        
        for key in bp.keys():
            plt.setp(bp[key], color='black', lw=1)
        
        # Adjust the power limits so that you use scientific notation on the y axis
        plt.ticklabel_format(style='sci', axis='y')
        ax.yaxis.major.formatter.set_powerlimits((-3,3))

        plt.ylabel(measures_names[i])
        
        for t in ax.yaxis.get_major_ticks(): 
            t.tick1On = False 
            t.tick2On = False 
                     
        # Get the y axis limits
        ymin, ymax = plt.ylim()
        yrange = ymax - ymin
        
        if ttest:
        
            # This section of code plots a line between two of the measures
            # and also assigns ns, *, ** or *** according to the two tailed
            # t-test for that pair of measures.
            
            # First, you need to know how many tests you're going to conduct
            # You can probably calcuate this but we're actually just going to
            # loop through and get a little counter going
            n_combo=0
            
            for combo in it.combinations(range(len(df_list)), 2):
                n_combo+=1
        
            # Get the y axis limits
            ymin, ymax = plt.ylim()
            yrange = ymax - ymin
            
            # Now we're going to calculate where all the various lines are going
            # to go for these tests:
            step_up = yrange * 0.1
            
            # Make the y axis run from just below the ymin, and increase
            # the max to one step above (ymax + step_up * n_combos)
            plt.ylim(ymin - 0.1*yrange, ymax + (step_up * (n_combo + 1)))

            # Start a counter for the combinations
            counter=0
            
            # Now loop through the combinations again but calculate the t-test statistic
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
                    
                print a, b, test_name

    # Make sure the layout looks good :)        
    fig.tight_layout()
    
    return fig

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
