#!/usr/bin/env python

def create_violin_plots(df_list, measures_list, measures_names, height, group_names, ttest=False):
    import matplotlib.pylab as plt
    import numpy as np
    import statsmodels.api as sm
    from scipy import stats
    from matplotlib.ticker import MaxNLocator

    
    fig = plt.figure(figsize=(height*len(measures_list), height))
    
    font = { 'size'   : 22 * height/8}

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
        plt.ylim(ymin - 0.1*yrange, ymax+0.1*yrange)
                  
        if ttest:
        
            # Calculate Bartlett test of equal variance
            t_var, p_var = stats.bartlett(df_list[0][measure], df_list[1][measure])
            
            # Calculate the ttest results
            if p_var < 0.05:
                t, p = stats.ttest_ind(df_list[0][measure], df_list[1][measure], equal_var=False)
            else:
                t, p = stats.ttest_ind(df_list[0][measure], df_list[1][measure])
            
            # Figure out the text you're going to put on the plot
            star = 'ns'
            if 0.01 < p < 0.05:
                star = '*'
            elif 0.001 <= p < 0.01:
                star = '**'
            elif p < 0.001:
                star = '***'
                                
            # Get the y axis limits
            ymin, ymax = plt.ylim()
            plt.ylim(ymin, ymax*1.1)
            
            # Plot the t-test line halfway between the max value
            # and the top of the plot
            measure_max = df_list[0][measure].max()
            for df in df_list:
                if df[measure].max() > measure_max:
                    measure_max = df[measure].max()
            
            y = (ymax*1.1 + measure_max) /2.0
            drop = (ymax - ymin)/50

            plt.plot([1.0, 2.0], [y, y], color='k')
            plt.plot([1.0, 1.0], [y, y-drop], color='k')
            plt.plot([2.0, 2.0], [y, y-drop], color='k')
            text = ax.text(1.5, y, star,
                horizontalalignment='center',
                verticalalignment='bottom',
                color = 'k')
        

    # Make sure the layout looks good :)        
    fig.tight_layout()
    
    return fig

