#!/usr/bin/env python

def create_stats_dict(df, group_var, continuous_measures=None, discrete_measures=None):
    '''
    This function first groups the data frame (df) by the grouping variable (group_var)
    
    It then loops through the discrete and continuous measures and tests the two groups
    for equality of means and variances. 

    Next, the contiuous measures and discrete measures are all pairwise correlated 
    for each group separately and the whole group together.

    All data is stored in the returned dictionary (stats_dict).
    '''
    
    import pandas as pd
    import numpy as np
    from scipy.stats import ttest_ind, bartlett, fisher_exact, pearsonr
    import itertools as it

    stats_dict = {}
    
    grouped = df.groupby(group_var)
    
    # Loop first through the discrete measures
    if discrete_measures:
        for measure in discrete_measures[0]:
            grouped_again = df.groupby([group_var, measure])
            key = '_'.join([group_var, measure, 'n'])
            stats_dict[key] = grouped_again[measure].count().values[:]
            
            if len(np.array(grouped_again[measure].count())) == 4:
                # Now calculate the Fisher's exact test on this contingency table
                n_array = np.array(grouped_again[measure].count()).reshape([2,2])
                
                key = '_'.join([group_var, measure, 'fisher'])
                stats_dict[key] = fisher_exact(n_array)
               
    # Loop through the continuous measures
    if continuous_measures:
        for measure in continuous_measures:
            
            # Save some basic stats for each measure by group
            key = '_'.join([measure, 'n'])
            stats_dict[key] = grouped[measure].count().values[:]
            
            key = '_'.join([measure, 'mean'])
            stats_dict[key] = grouped[measure].mean().values[:]
            
            key = '_'.join([measure, 'std'])
            stats_dict[key] = grouped[measure].std().values[:]
            
            # Now save the output of tests of equal variance
            # and equal means
            
            values = [ g.values for n, g in grouped[measure] ]
    
            values[0] = [ x for x in values[0] if not np.isnan(x) ]
            values[1] = [ x for x in values[1] if not np.isnan(x) ]
    
            # Conduct test for equal variance
            key = '_'.join([measure, 'eq_var'])
            stats_dict[key] = bartlett(values[0], values[1])
            
            # When you test for equal means (ttest) you have different options
            # depending on if you have equal variances or not
            if stats_dict[key][1] < 0.05:
                # Conduct Welch's t-test (unequal variances)
                key = '_'.join([measure, 'eq_means'])        
                stats_dict[key] = ttest_ind(values[1], values[0], equal_var = False)
            
            else:
                # Conduct standard t-test (equal variances)
                key = '_'.join([measure, 'eq_means'])        
                stats_dict[key] = ttest_ind(values[1], values[0], equal_var = True)
            
        # PAIRWISE CORRELATIONS
        if continuous_measures:
            for a, b in it.combinations(continuous_measures,2):
                # First look at the whole group
                mask = (df[a] > 0) * (df[b] > 0)
                key = '_'.join([group_var, 'all', a, b, 'n'])
                stats_dict[key] = np.sum(mask)
    
                a_values = df[a][mask].values
                b_values = df[b][mask].values
                key = '_'.join([group_var, 'all', a, b, 'pwcorr'])
                stats_dict[key] = pearsonr(a_values, b_values)
                
                # Then for the groups individually
                for name, group in grouped:
                    mask = (group[a] > 0) * (group[b] > 0)
                    key = '_'.join([group_var, str(name), a, b, 'n'])
                    stats_dict[key] = np.sum(mask)
    
                    a_values = group[a][mask].values
                    b_values = group[b][mask].values
                    key = '_'.join([group_var, str(name), a, b, 'pwcorr'])
                    stats_dict[key] = pearsonr(a_values, b_values)
            
            # TTESTS between continuous measures and discrete variables
            if discrete_measures:
                for discrete, a in it.product(discrete_measures[0], continuous_measures):
                    # First look at the whole group
                    grouped_discrete = df.groupby(discrete)
                    
                    values = [ g.values for n, g in grouped_discrete[a] ]

                    if len(values) == 2:

                        values[0] = [ x for x in values[0] if not np.isnan(x) ]
                        values[1] = [ x for x in values[1] if not np.isnan(x) ]
        
                        # Conduct test for equal variance
                        key = '_'.join([group_var, 'all', discrete, a, 'eq_var'])
                        stats_dict[key] = bartlett(values[0], values[1])
                        
                        # When you test for equal means (ttest) you have different options
                        # depending on if you have equal variances or not
                        if stats_dict[key][1] < 0.05:
                            # Conduct Welch's t-test (unequal variances)
                            key = '_'.join([group_var, 'all', discrete, a, 'eq_means'])        
                            stats_dict[key] = ttest_ind(values[1], values[0], equal_var = False)
                        
                        else:
                            # Conduct standard t-test (equal variances)
                            key = '_'.join([group_var, 'all', discrete, a, 'eq_means'])        
                            stats_dict[key] = ttest_ind(values[1], values[0], equal_var = True)
                    
                    # Next look at the two groups separately:
                    for name, group in grouped:
                        grouped_discrete = group.groupby(discrete)
                                                
                        values = [ g.values for n, g in grouped_discrete[a] ]
                        
                        if len(values) == 2:
                            
                            values[0] = [ x for x in values[0] if not np.isnan(x) ]
                            values[1] = [ x for x in values[1] if not np.isnan(x) ]
            
                            # Conduct test for equal variance
                            key = '_'.join([group_var, str(name), discrete, a, 'eq_var'])
                            stats_dict[key] = bartlett(values[0], values[1])
                            
                            # When you test for equal means (ttest) you have different options
                            # depending on if you have equal variances or not
                            if stats_dict[key][1] < 0.05:
                                # Conduct Welch's t-test (unequal variances)
                                key = '_'.join([group_var, str(name), discrete, a, 'eq_means'])        
                                stats_dict[key] = ttest_ind(values[1], values[0], equal_var = False)
                            
                            else:
                                # Conduct standard t-test (equal variances)
                                key = '_'.join([group_var, str(name), discrete, a, 'eq_means'])        
                                stats_dict[key] = ttest_ind(values[1], values[0], equal_var = True)

        if discrete_measures:
            if len(discrete_measures) > 1:
                for a, b in it.combinations(discrete_measures[0], 2):
                    # Look first at the whole group
                    grouped_again = df.groupby([a,b])
                    
                    if len(np.array(grouped_again[b].count())) == 4:
                    
                        key = '_'.join([group_var, 'all', a, b, 'n'])
                        stats_dict[key] = grouped_again[b].count().values[:]
                        
                        # Now calculate the Fisher's exact test on this contingency table
                        n_array = np.array(grouped_again[b].count()).reshape([2,2])
                    
                        key = '_'.join([group_var, 'all', a, b, 'fisher'])
                        stats_dict[key] = fisher_exact(n_array)
        
                        # Now loop through the two groups separately
                        for name, group in grouped:
                            grouped_again = group.groupby([a,b])
                            
                            if len(np.array(grouped_again[b].count())) == 4:
                                
                                key = '_'.join([group_var, 'all', a, b, 'n'])
                                stats_dict[key] = grouped_again[b].count().values[:]
                                
                                # Now calculate the Fisher's exact test on this contingency table
                                n_array = np.array(grouped_again[b].count()).reshape([2,2])
                                
                                key = '_'.join([group_var, 'all', a, b, 'fisher'])
                                stats_dict[key] = fisher_exact(n_array)
                    
    return stats_dict