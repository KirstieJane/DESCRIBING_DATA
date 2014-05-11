#!/usr/bin/env python

def calc_stats(df, measures):

    # Import what you need
    import numpy as np
    from statsmodels.formula.api import ols, logit
    from scipy.stats import pearsonr

    # Set up the empty arrays that you're interested in
    (pairP_mat, pairES_mat, 
                partP_mat, partES_mat) = setup_arrays(measures)
        
  # Loop through all the measures
    for i, y in enumerate(measures):

        # Your covars are all the measures that aren't y
        covars = [x for x in measures if not x == y]
        
        # Your multiple regression formula is just a
        # linear regression of all the covars on y
        RHS = ' + '.join(covars)
        formula_all = '{} ~ {}'.format(y, RHS)
        
        # Fit the appropriate model
        lm_all = fit_model(y, formula_all, df)
        
        # Now to fill in the six different matrices
        # for all the "j" columns of this "i"th row
        for j, x in enumerate(measures):
            
            # Set all the matrix element values equal to 1 
            # if you're filling in the diagonal of the matrix
            if not i == j:
                # Calculate the ols regression or logistic
                # regression for just this pair of variables
                formula_pair = '{} ~ {}'.format(y, x)
                
                lm_pair = fit_model(y, formula_pair, df)
            
                # Fill in the correct p values
                pairP_mat[i ,j] = lm_pair.pvalues[x]
                partP_mat[i, j] = lm_all.pvalues[x]
                
                # Now fill in the effect size values
                if df[y].nunique() == 2:
                    pairES_mat[i, j] = np.exp(lm_pair.params)[x]
                    partES_mat[i, j] = np.exp(lm_all.params)[x]
                else:
                    pairES_mat[i, j] = pearsonr(df[x], df[y])[0]
                    print pairES_mat[i,j], np.sqrt(lm_pair.rsquared)
                    partES_mat[i, j] = partial_correlation(df, x, y, measures)[0]
                    
    return (pairP_mat, pairES_mat, 
                partP_mat, partES_mat)

    
def mask_triangle():
    # Create a mask of only the lower triangle and the diagonal
    mask = np.triu(empty_array, k=1)

def setup_arrays(measures):
    import numpy as np
    # Create an array of ones that's the appropriate size
    ones_array = np.ones([len(measures), len(measures)])

    # There are a few arrays we want to make
    # specifically pairwise comparisons and partial comparisons
    # and we'll save the R (if OLS), odds ratio (if logistic)
    # and P values (for both)
    pairES_mat = np.copy(ones_array)
    pairP_mat = np.copy(ones_array)
    
    partES_mat = np.copy(ones_array)
    partP_mat = np.copy(ones_array)

    return (pairP_mat, pairES_mat, 
                partP_mat, partES_mat)

def fit_model(y, formula, df):
    from statsmodels.formula.api import ols, logit

    # If you have a dichotomous variable then
    # we're going to run a logistic regression
    if df[y].nunique() == 2:
        lm = logit(formula, df).fit()
    # otherwise we'll run an ordinary least
    # squares regression
    else:
        lm = ols(formula, df).fit()

    return lm
    
def partial_correlation(df, x, y, measures):
    
    # Import pearson correlation
    from scipy.stats import pearsonr
    from statsmodels.formula.api import ols

    # Your covars are all the measures you've selected
    # that aren't x and y
    covars = [ z for z in measures if not z == x and not z == y ]
                                
    # Your formulae just set x and y to be a function
    # of all the other covariates
    formula_x = x + ' ~ ' + ' + '.join(covars)
    formula_y = y + ' ~ ' + ' + '.join(covars)

    # Fit both of these formulae
    lm_x = ols(formula_x, df).fit()
    lm_y = ols(formula_y, df).fit()
        
    # Save the residuals from the model
    res_x = lm_x.resid
    res_y = lm_y.resid
            
    r, p = pearsonr(res_x, res_y)
    
    return r, p


def plot_matrix(df_list, measures, names, height, group_names_short, star=False):
    
    # Import the various modules that you need
    import numpy as np
    import matplotlib.pylab as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    from scipy.stats import pearsonr
    from statsmodels.formula.api import ols, logit
    import matplotlib.colors as colors
    
    # Make a figure
    fig = plt.figure(figsize=(height*len(df_list), height))

    # Set a sensible sized font
    font = { 'size'   : 22 * height/10}
    plt.rc('font', **font)

    # Make separate plots for the df_lists:
    for c, df in enumerate(df_list):
        
        # Add a new axis for each df_list
        ax = fig.add_subplot(1,len(df_list), c+1)

        # Calculate the number of measures in the list
        N = len(measures)

        # Calculate the pairwise and partial statistic matrices
        (pairP_mat, pairES_mat, 
                partP_mat, partES_mat)  = calc_stats(df, measures)
                  
        maskO = np.ones_like(pairES_mat)
        maskR = np.ones_like(pairES_mat)
        
        for y in measures:
            if df[y].nunique() == 2:
                print y
                maskO[measures.index(y),:] = 0
            else:
                maskR[measures.index(y),:] = 0

        # Create a mask of only the lower triangle and the diagonal
        maskTri = np.triu(pairES_mat, k=1)
        
        print pairES_mat
        print pairP_mat
        
        # Add this mask to the R and O masks. The reason you add these
        # is because in the next step we're going to only plot
        # values that have a mask value of 0
        # maskR = maskR + maskTri
        # maskO = maskO + maskTri

        # Mask the effect size matrices
        mpairO = np.ma.masked_array(pairES_mat, mask=maskO)
        mpairR = np.ma.masked_array(pairES_mat, mask=maskR)

        # Make the background grey
        pbg = plt.imshow(np.ones_like(pairES_mat)*0.5, cmap='Greys', vmin=0, vmax=1, interpolation='none')
        
        # Plot the pairwise effect size map
        r = plt.imshow(mpairR, cmap = 'RdBu_r', vmin=-1, vmax=1, interpolation='none')
        o = plt.imshow(mpairO, cmap = 'PRGn', vmin=0.2, vmax=5, interpolation='none', norm=colors.LogNorm(vmin=0.02, vmax=5))

        # Make the diagonal line black
        eye_mat = np.eye(mpairR.shape[0])
        meye = np.ma.masked_array(eye_mat, 1 - eye_mat)
        eye = plt.imshow(meye, cmap='Greys', vmin=0, vmax=1, interpolation='none')
        
        # Make your tick_labels line up sensibly
        locs = np.arange(0, float(N))
        ax.set_xticks(locs)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.set_yticks(locs)
        ax.set_yticklabels(names)

        # Set up TWO lovely color bars
        divider = make_axes_locatable(plt.gca())
        
        tick_labels = [ '{: 1.1f}'.format(tick) for tick in list(np.linspace(-1,1,5)) ]
        cax_r = divider.append_axes("right", "5%", pad="12%")
        cbar_r = fig.colorbar(r, cax=cax_r, ticks = list(np.linspace(-1,1,5)))
        cax_r.set_yticklabels(tick_labels) 
        cax_r.set_ylabel('Pearson r', size='small')
        cax_r.yaxis.set_label_position("left")

        tick_labels = [ '{: 1.1f}'.format(tick) for tick in list(np.logspace(np.log(0.2), np.log(5), 5, base=np.e)) ]
        cax_o = divider.append_axes("right", "5%", pad="25%")
        cbar_o = fig.colorbar(o, cax=cax_o, ticks = list(np.logspace(np.log(0.2), np.log(5), 5, base=np.e)))
        cax_o.set_yticklabels(tick_labels)
        cax_o.set_ylabel('Odds ratio', size='small')
        cax_o.yaxis.set_label_position("left")

        # Give your plot a lovely title
        ax.set_title(group_names_short[c])
    
        if star:
        
            # Loop through all the measures and fill the arrays
            i_inds, j_inds = np.triu_indices_from(pairES_mat, k=-3)
            for i, j in zip(i_inds, j_inds):

                # Figure out the text you're going to put on the plot
                star = ''
                if 0.01 < pairP_mat[i,j] < 0.05:
                    star = '*'
                elif 0.001 <= pairP_mat[i,j] < 0.01:
                    star = '**'
                elif pairP_mat[i,j] < 0.001:
                    star = '***'

                text = ax.text(i, j, star,
                    horizontalalignment='center',
                    verticalalignment='center',
                    color = 'k')
        
    #plt.tight_layout()

    return fig

