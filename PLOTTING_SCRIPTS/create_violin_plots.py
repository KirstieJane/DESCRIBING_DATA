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
                                plot_opts = { 'violin_fc':plt.cm.Greens(.7) ,
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
                
                # Calculate Bartlett test of equal variance
                t_var, p_var = stats.bartlett(df_list[a][measure], df_list[b][measure])
                
                # Calculate the ttest results
                if p_var < 0.05:
                    t, p = stats.ttest_ind(df_list[a][measure], df_list[b][measure], equal_var=False)
                else:
                    t, p = stats.ttest_ind(df_list[a][measure], df_list[b][measure])
                
                # Figure out the text you're going to put on the plot
                star = 'ns'
                if 0.01 < p < 0.05:
                    star = '*'
                elif 0.001 <= p < 0.01:
                    star = '**'
                elif p < 0.001:
                    star = '***'
                
                '''                                    
                # Plot the t-test line halfway between the max value
                # and the top of the plot
                measure_max = df_list[0][measure].max()
                for df in df_list:
                    if df[measure].max() > measure_max:
                        measure_max = df[measure].max()
                '''
                # We're going to plot the line that shows which test you're conducting
                # at increments of the step up measure
                y = (counter - 0.5) * step_up + ymax
                '''
                # We're going to plot the line that shows which test you're conducting
                # halfway between the ymax * 1.1 and the measure_max
                y = (ymax*1.1 + measure_max) / 2.0
                '''
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
        

    # Make sure the layout looks good :)        
    fig.tight_layout()
    
    return fig

