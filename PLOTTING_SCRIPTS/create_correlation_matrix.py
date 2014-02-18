#!/usr/bin/env python

def create_partial_correlation_matrix(df_list, measures, names, height, group_names_short, star=False):
    
    # Import the various modules that you need
    import numpy as np
    import matplotlib.pylab as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    from scipy.stats import pearsonr
    from statsmodels.formula.api import ols

    # Make a figure
    fig = plt.figure(figsize=(height*len(df_list), height))

    # Set a sensible sized font
    font = { 'size'   : 22 * height/18}
    plt.rc('font', **font)

    # Make separate plots for the df_lists:
    for c, df in enumerate(df_list):
        
        # Add a new axis for each df_list
        ax = fig.add_subplot(1,len(df_list), c+1)

        # Calculate the number of measures in the list
        N = len(measures)

        # Calculate the correlation matrix
        R = df[measures].corr().values
        
        # Create a mask of only the lower triangle and the diagonal
        mask = np.triu(R, k=1)

        # Create two empty arrays ready to hold the r and p values
        # for the partial correlation matrix
        partp_mat = np.ones_like(R)
        partr_mat = np.ones_like(R)
        
        # Loop through all the measures and fill the arrays
        i_inds, j_inds = np.triu_indices_from(R, k=1)
        for i, j in zip(i_inds, j_inds):
            
            covars = list(measures)
            
            x = covars.pop(i)
            y = covars.pop(j-1)
            
            formula_x = x + ' ~ ' + ' + '.join(covars)
            formula_y = y + ' ~ ' + ' + '.join(covars)

            lm_x = ols(formula_x, df).fit()
            res_x = lm_x.resid
            lm_y = ols(formula_y, df).fit()
            res_y = lm_y.resid
            
            partr_mat[i,j], partp_mat[i,j] = pearsonr(res_x, res_y)
            partr_mat[j,i], partp_mat[j,i] = pearsonr(res_x, res_y)
            
        mpartR = np.ma.masked_array(partr_mat, mask=mask)

        pbg = plt.imshow(np.ones_like(R)*0.5, cmap='Greys', vmin=0, vmax=1, interpolation='none')
        
        ### Not the pairwise correlations but the partial correlation map
        pc = plt.imshow(mpartR, cmap = 'RdBu_r', vmin=-1, vmax=1, interpolation='none')
        
        divider = make_axes_locatable(plt.gca())
        cax = divider.append_axes("right", "5%", pad="3%")
        tick_labels = [ '{: 1.1f}'.format(tick) for tick in list(np.linspace(-1,1,5)) ]

        cbar = fig.colorbar(pc, cax=cax, ticks = list(np.linspace(-1,1,5)))
        cax.set_yticklabels(tick_labels) 

        locs = np.arange(0, float(N))
        
        ax.set_xticks(locs)
        ax.set_xticklabels(names, rotation=45, ha='right')
        
        ax.set_yticks(locs)
        ax.set_yticklabels(names)

        ax.set_title(group_names_short[c])
    
        if star:
        
            # Loop through all the measures and fill the arrays
            i_inds, j_inds = np.triu_indices_from(R, k=1)
            for i, j in zip(i_inds, j_inds):

                # Figure out the text you're going to put on the plot
                star = ''
                if 0.01 < partp_mat[i,j] < 0.05:
                    star = '*'
                elif 0.001 <= partp_mat[i,j] < 0.01:
                    star = '**'
                elif partp_mat[i,j] < 0.001:
                    star = '***'

                text = ax.text(i, j, star,
                    horizontalalignment='center',
                    verticalalignment='center',
                    color = 'k')
        
    plt.tight_layout()

    return fig

def create_correlation_matrix(df_list, measures, names, height, group_names_short, star=False):
    
    import numpy as np
    import matplotlib.pylab as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    from scipy.stats import pearsonr

    fig = plt.figure(figsize=(height*len(df_list), height))

    font = { 'size'   : 22 * height/18}

    plt.rc('font', **font)

    # Make separate plots for the df_lists:
    for i, df in enumerate(df_list):
        
        ax = fig.add_subplot(1,len(df_list), i+1)

        N = len(measures)

        R = df[measures].corr().values
        
        mask = np.triu(R, k=1)
        mR = np.ma.masked_array(R, mask=mask)
        
        pbg = plt.imshow(np.ones_like(R)*0.5, cmap='Greys', vmin=0, vmax=1, interpolation='none')
        pc = plt.imshow(mR, cmap = 'RdBu_r', vmin=-1, vmax=1, interpolation='none')
        
        divider = make_axes_locatable(plt.gca())
        cax = divider.append_axes("right", "5%", pad="3%")
        tick_labels = [ '{: 1.1f}'.format(tick) for tick in list(np.linspace(-1,1,5)) ]

        cbar = fig.colorbar(pc, cax=cax, ticks = list(np.linspace(-1,1,5)))
        cax.set_yticklabels(tick_labels) 

        locs = np.arange(0, float(N))
        
        ax.set_xticks(locs)
        ax.set_xticklabels(names, rotation=45, ha='right')
        
        ax.set_yticks(locs)
        ax.set_yticklabels(names)

        ax.set_title(group_names_short[i])
    
        if star:
        
            # Create two empty arrays ready to hold the r and p values
            p_mat = np.ones_like(df[measures].corr().values)
            r_mat = np.ones_like(df[measures].corr().values)
            
            # Loop through all the measures and fill the arrays
            i_inds, j_inds = np.triu_indices_from(R, k=1)
            for i, j in zip(i_inds, j_inds):
                r_mat[i,j], p_mat[i,j] = pearsonr(df[measures[i]].values, df[measures[j]].values)


                # Figure out the text you're going to put on the plot
                star = ''
                if 0.01 < p_mat[i,j] < 0.05:
                    star = '*'
                elif 0.001 <= p_mat[i,j] < 0.01:
                    star = '**'
                elif p_mat[i,j] < 0.001:
                    star = '***'

                text = ax.text(i, j, star,
                    horizontalalignment='center',
                    verticalalignment='center',
                    color = 'k')
        
        
    plt.tight_layout()

    return fig
