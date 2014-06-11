#!/usr/bin/env python

def scatter_interaction(ax, x, y, groups, colors, ms=5, labels=None, title=None, legend=False, formula='y ~ x'):
    
    # Here are the imports
    import numpy as np
    import matplotlib.pylab as plt
    import pandas as pd
    from scipy.stats import pearsonr
    from statsmodels.sandbox.regression.predstd import wls_prediction_std
    from statsmodels.formula.api import ols
    from statsmodels.stats.outliers_influence import summary_table

    # If you haven't already been given an axis on which to plot, then
    # create a new figure
        
    if not ax:
        fig = plt.figure(figsize = (5,4))
        
        ax = fig.add_subplot(111)
    
    marker_styles = [ 'o', '^', 'D', 's', '*' ] * len(groups)
    line_styles = ['--', '-', '-.', ':'] * len(groups)
    
    # Loop through all the groups
    for i, x_i, y_i, c_i, g_i, m_i, l_i in zip(range(len(groups)), x, y, colors, groups, marker_styles, line_styles):

        # Scatter each with the appropriate colors
        ax.scatter(x_i, y_i, c=c_i, edgecolor=c_i, alpha=0.8, s=ms, marker=m_i, zorder=7*i)
        
        # Now calculate the linear correlation between x and y
        # for each group
        # Heavily stolen from:
        # http://www.students.ncl.ac.uk/tom.holderness/software/pythonlinearfit
        #z = np.polyfit(x_i,y_i,1)
        #p = np.poly1d(z)
        #fit = p(x_i)
        #c_x = [np.min(x_i),np.max(x_i)]
        #c_y = [p(np.min(x_i)), p(np.max(x_i))]

        df2 = pd.DataFrame({ 'x' : x_i, 'y' : y_i })
        df2.sort('x', inplace=True)
        lm = ols(formula, df2).fit()
        ps = [ '{:2.4f}'.format(p) for p in lm.pvalues[1:] ]
        print '    r2 = {}, p(s) = {}'.format(lm.rsquared, ', '.join(ps))
        prstd, iv_l, iv_u = wls_prediction_std(lm)
        iv_l = np.array(iv_l)
        iv_u = np.array(iv_u)
        fit_y = np.array(lm.fittedvalues)
        st, data, ss2 = summary_table(lm, alpha=0.05)

        predict_mean_ci_low, predict_mean_ci_upp = data[:,4:6].T

        #pl.plot(x, y, 'k-')
        #pl.plot(x, fit_y, 'r--')
        #pl.fill_between(x, iv_l, iv_u, alpha=0.2)
        
        # Get the r and p values
        #r, p = pearsonr(x_i, y_i)
        #label = '{} r: {: .2g} p: {: .2g}'.format(g_i, r, p)
        # Now plot
        ax.plot(df2.x.values, fit_y, c=c_i, linestyle = '-', linewidth = ms/25.0, zorder=6*i, label=g_i)
        ax.plot(df2.x.values, predict_mean_ci_low, c=c_i, linestyle = '-', linewidth = ms/50.0, zorder=3*i)
        ax.plot(df2.x.values, predict_mean_ci_upp, c=c_i, linestyle = '-', linewidth = ms/50.0, zorder=2*i)
        ax.fill_between(df2.x.values, predict_mean_ci_upp, predict_mean_ci_low, alpha=0.3, facecolor=c_i, interpolate=True, zorder=1*i)
        
    if legend:
        # Add the legend
        leg = ax.legend(loc='best', fancybox=True, fontsize=ms/5.)
        leg.get_frame().set_alpha(0)

    # Set the y limits
    # This is to deal with very small numbers (the MaxNLocator gets all turned around!)
    # Concatenate all the y data:
    y_all = y[0]
    if len(y) > 1:
        for k in range(1,len(y)):
            y_all = np.concatenate([y_all, y[k]])
    max_y = np.max(y_all)
    min_y = np.min(y_all)
    buffer = ( max_y - min_y ) / 10
    upper = max_y + buffer
    lower = min_y - buffer
    ax.set_ybound(upper, lower)
    
    # Set the axis labels    
    ax.set_ylabel(labels[1], fontsize=ms/5.0)
    ax.set_xlabel(labels[0], fontsize=ms/5.0)
    
    for item in (ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(ms/5.0)
    # Adjust the power limits so that you use scientific notation on the y axis
    plt.ticklabel_format(style='sci', axis='y')
    ax.yaxis.major.formatter.set_powerlimits((-3,3))
    
    plt.rc('font', **{'size':ms/5.0})
    
    if title:
        # Set the overall title
        ax.set_title(title)

    plt.tight_layout()
    
    return ax

def get_fig(height, layout='one_large_three_small'):
    
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
        ax = [ ax1, ax2, ax3, ax4 ]

        msizes = [ 50, 15, 15, 15 ] # Marker sizes
    
    if layout == 'four_equal_size_one_row':
        # Generate a figure
        fig = plt.figure(figsize = (4*height, height))
        
        # Create four subplots
        ax1 = plt.subplot2grid((1,4), (0,0))
        ax2 = plt.subplot2grid((1,4), (0,1))
        ax3 = plt.subplot2grid((1,4), (0,2))
        ax4 = plt.subplot2grid((1,4), (0,3))
    
        msizes = [ 15, 15, 15, 15 ] # Marker sizes
        
        # Create your axes list
        ax = [ ax1, ax2, ax3, ax4 ]
        
    if layout == 'just_one':
        # Generate a figure
        fig = plt.figure(figsize = (height*1.5, height))

        # Add just one subplot
        ax1 = plt.axes()
        
        ax = [ ax1 ]
        
        msizes = [ 10 ]
        
    # Set the marker sizes
    msizes = [ m * height for m in msizes ]
    
    return fig, ax, msizes

def plot_scatter_dtimeasures(df_list, x, y, groups, height, labels, title, plot_colors, grid_layout='one_large_three_small', legend=False, formula='y ~ x'):
    """
    This code takes in a list of pandas data frames, and creates
    four plots - one large and 3 small to the right - one for each of
    the four dti measures.
    
    The figure ends up being 4 * height by 3 * height in size
    
    Alternatively it can just plot one if you say "just_one"
    for the grid layout
    
    x is just one x variable which will be the same for all plots
    y is a list of y variables eg: [ fa, md, l1, l23 ]
    
    """
    
    # Here are the imports you need
    import matplotlib.pylab as plt
    import numpy as np
    import pandas as pd
    
    # Get the figure and appropriate grid layout
    fig, ax, msizes = get_fig(height, grid_layout)
    
    # Loop through all the measures in the df_list
    for i in range(len(ax)):
        # Initalize the x and y data lists as empty
        x_list = list()
        y_list = list()
        
        # Get the data separately for each group
        for j, df in enumerate(groups):
            x_list.append(df_list[j][x])
            y_list.append(df_list[j][y[i]])

        # Use the scatter interaction code to plot both groups
        # onto the appropriate plot

        ax[i] = scatter_interaction(ax=ax[i], x = x_list, y = y_list,
                        groups = groups,
                        colors = plot_colors,
                        labels = [labels[0], labels[i+1]],
                        ms = msizes[i],
                        legend=legend,
                        formula=formula)

    if title:
        # Give the figure a title
        fig.suptitle(title, fontsize=msizes[0]/2.0)
        # And give it a bit more room at the top
        plt.subplots_adjust(top=0.9)
    
    return fig, ax[i]
    
