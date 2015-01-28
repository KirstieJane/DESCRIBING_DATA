#!/usr/bin/env python

def create_bar_plots(bins, freq_list, height, group_names, colors, xlabel, ylabel, legend=True):
    import matplotlib.pylab as plt
    import numpy as np
    from matplotlib.ticker import MaxNLocator
    
    fig = plt.figure(figsize=(height*1.5, height))
    ax = fig.add_subplot(111)
    
    font = { 'size'   : 22 * height/8}

    plt.rc('font', **font)
    
    range = np.max(bins) - np.min(bins)
    w = range/((len(bins)-1) * len(group_names))

    for i, group in enumerate(group_names):
        
        bar = plt.bar(bins + w*i, freq_list[i],
                                width=w, label = group,
                                color=colors[i],
                                edgecolor='none')
        
        # Adjust the power limits so that you use scientific notation on the y axis
        plt.ticklabel_format(style='sci', axis='y')
        ax.yaxis.major.formatter.set_powerlimits((-3,3))

        for t in ax.yaxis.get_major_ticks(): 
            t.tick1On = False 
            t.tick2On = False 

    if legend:
        plt.legend(loc=0)
    
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    # Make sure the layout looks good :)        
    fig.tight_layout()
    
    return fig

