#!/usr/bin/env python

def create_stats_dict(df, group_var, continuous_measures=None, discrete_measures=None):
    '''
    This function first groups the data frame (df) by the grouping variable (group_var)
    
    It then loops through the discrete and continuous measures and tests the two groups
    for equality of means and variances. 

    Next, the continous measures and discrete measures are all compared
    for each group separately and the whole group together.

    All data is stored in the returned dictionary (stats_dict).
    For the discrete measures there are the following entries:
        * KEY: Number of participants, eg: Meds_male_n 
          VALUE: Contingency table of the number of people
                 in each combination of group_var and discrete measure
                 
        * KEY: Output of fisher's exact test, eg: Meds_male_fisher
          VALUE: odds_ratio and p_value tuple 
    
    For the continuous measures there are the following entries:
        * KEY: Number of observations, eg: Age_mean
          VALUE: Number of observations in each group of group_var
        
        * KEY: Mean value, eg: Age_mean
          VALUE: Mean value for the continuous measure
                 for each group of group_var

        * KEY: Standard deviation, eg: Age_std
          VALUE: Sandard deviation for the continuous measure
                 for each group of group_var
                 
        * KEY: Percentile_values, eg: Age_perc25, Age_perc50, Age_perc75
          VALUE: 25th, 50th and 75th percentile values 
                 for the continuous measure for each group of group_var
                 
        * KEY: Median value, eg: Age_perc50
          VALUE: Median value for the continuous measure
                 for each group of group_var

        * KEY: Test of equal variance output, eg: Age_eqvar
          VALUE: t and p values for bartlett test of equal variance

        * KEY: Test of normality, eg: Age_normal
          VALUE: k2 and p values for omnibus test of normality for *ungrouped* data
          
        * KEY: Test of equal means given equal variance output, eg: Age_ttest_eqvar
          VALUE: t and p values for student's t-test

        * KEY: Test of equal means given unequal variance output, eg: Age_ttest_uneqvar
          VALUE: t and p values for Welsch's t-test

        * KEY: Test of equal medians, eg: Age_mannwhitneyu
          VALUE: U and p values for Mann Whitney U test
    '''
    
    # Import what you need
    import numpy as np
    from scipy.stats import ttest_ind, bartlett, fisher_exact, pearsonr, mannwhitneyu, normaltest
    import itertools as it

    # Create the stats dictionary that we're going to fill in
    stats_dict = {}
    
    # Group the data frame by the grouping variable
    grouped = df.groupby(group_var)
    
    # Loop first through the discrete measures (if there are any)
    if discrete_measures:
        
        for measure in discrete_measures[0]:
            
            # Group the data frame by BOTH the grouping variable 
            # and the discrete measure
            grouped_again = df.groupby([group_var, measure])

            # Define the key for "n" entry to the stats dictionary
            key = '_'.join([group_var, measure, 'n'])
            
            # Add the number of members of each group into the stats_dict
            stats_dict[key] = grouped_again[measure].count().values[:]
            
            # If you have members in each of the four groups then
            # calculate the Fisher's exact test on this contingency table
            if len(np.array(grouped_again[measure].count())) == 4:
                
                # The n_array is the contingency table
                n_array = np.array(grouped_again[measure].count()).reshape([2,2])
                
                # Define the key for the dictionary entry
                key = '_'.join([group_var, measure, 'fisher'])
                
                # And add the fisher's exact output to the stats_dict
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
            
            key = '_'.join([measure, 'perc25'])
            stats_dict[key] = grouped[measure].quantile(0.25).values[:]
            
            key = '_'.join([measure, 'perc50'])
            stats_dict[key] = grouped[measure].quantile(0.5).values[:] 

            key = '_'.join([measure, 'median'])
            stats_dict[key] = grouped[measure].quantile(0.5).values[:] 
            
            key = '_'.join([measure, 'perc75'])
            stats_dict[key] = grouped[measure].quantile(0.75).values[:] 
            
            # Now save the output of tests of equal variance
            # and equal means
            
            # Use this snazzy little list manipulation to get the 
            # group values
            values = [ g.values for n, g in grouped[measure] ]
            
            # If there are two groups
            if len(values) == 2:

                # Mask out the not a numbers
                values[0] = [ x for x in values[0] if not np.isnan(x) ]
                values[1] = [ x for x in values[1] if not np.isnan(x) ]
        
                # Conduct test for equal variance
                key = '_'.join([measure, 'eqvar'])
                stats_dict[key] = bartlett(values[0], values[1])
                
                # Conduct test for normality
                key = '_'.join([measure, 'normal'])
                stats_dict[key] = normaltest(np.hstack([values[0], values[1]]))
                
                # When you test for equal means (ttest) you have different options
                # depending on if you have equal variances or not. You can also
                # run the non-parametric Mann Whitney U test
                
                # All three will be entered in the stats_dict
                
                # Conduct Welch's t-test (unequal variances)
                key = '_'.join([measure, 'ttest_uneqvar'])
                stats_dict[key] = ttest_ind(values[1], values[0], equal_var = False)
            
                # Conduct standard student's t-test (equal variances)
                key = '_'.join([measure, 'ttest_eqvar'])
                stats_dict[key] = ttest_ind(values[1], values[0], equal_var = True)

                # Conduct mann whitney U test (non-parametric test of medians)
                key = '_'.join([measure, 'mannwhitneyu'])
                u, p = mannwhitneyu(values[1], values[0])
                stats_dict[key] = (u, p*2)        
                
        # For two continuous measues we can calculate
        # PAIRWISE CORRELATIONS
        if continuous_measures:
            for a, b in it.combinations(continuous_measures,2):
                # First look at the whole group
                # mask out participants who don't have both measures
                mask = (df[a].notnull()) * (df[b].notnull())
                
                # Enter the number of participants that were included for the
                # regression into your stats dict
                key = '_'.join([group_var, 'all', a, b, 'n'])
                stats_dict[key] = np.sum(mask)
    
                # Figure out the pairwise correlation for this pair of measures
                # and add it to your stats_dict
                a_values = df[a][mask].values
                b_values = df[b][mask].values
                key = '_'.join([group_var, 'all', a, b, 'pwcorr'])
                stats_dict[key] = pearsonr(a_values, b_values)
                
                # Then do the same thing for the groups individually
                for name, group in grouped:
                    mask = (group[a].notnull()) * (group[b].notnull())
                    
                    # Save the number of members of the group who were 
                    # included in the regression
                    key = '_'.join([group_var, str(name), a, b, 'n'])
                    stats_dict[key] = np.sum(mask)
    
                    # And save the pairwise correlation
                    a_values = group[a][mask].values
                    b_values = group[b][mask].values
                    key = '_'.join([group_var, str(name), a, b, 'pwcorr'])
                    stats_dict[key] = pearsonr(a_values, b_values)
            
            # For a combination of a continous measure and a discrete measure
            # we can conduct TTESTS 
            if discrete_measures:
                for discrete, a in it.product(discrete_measures[0], continuous_measures):
                    # First look at the whole group
                    grouped_discrete = df.groupby(discrete)
                    
                    values = [ g.values for n, g in grouped_discrete[a] ]

                    if len(values) == 2:

                        # Mask out the not a numbers
                        values[0] = [ x for x in values[0] if not np.isnan(x) ]
                        values[1] = [ x for x in values[1] if not np.isnan(x) ]
                
                        # Conduct test for equal variance
                        key = '_'.join([group_var, 'all', discrete, a, 'eqvar'])
                        stats_dict[key] = bartlett(values[0], values[1])
                        
                        # Conduct test for normality
                        key = '_'.join([group_var, 'all', discrete, a, 'normal'])
                        stats_dict[key] = normaltest(np.hstack([values[0], values[1]]))
                        
                        # When you test for equal means (ttest) you have different options
                        # depending on if you have equal variances or not. You can also
                        # run the non-parametric Mann Whitney U test
                        
                        # All three will be entered in the stats_dict
                        
                        # Conduct Welch's t-test (unequal variances)
                        key = '_'.join([group_var, 'all', discrete, a, 'ttest_uneqvar'])
                        stats_dict[key] = ttest_ind(values[1], values[0], equal_var = False)
                    
                        # Conduct standard student's t-test (equal variances)
                        key = '_'.join([group_var, 'all', discrete, a, 'ttest_eqvar'])
                        stats_dict[key] = ttest_ind(values[1], values[0], equal_var = True)
        
                        # Conduct mann whitney U test (non-parametric test of medians)
                        key = '_'.join([group_var, 'all', discrete, a, 'mannwhitneyu'])
                        u, p = mannwhitneyu(values[1], values[0])
                        stats_dict[key] = (u, p*2)
                            
                    # Next look at the two groups separately:
                    for name, group in grouped:
                        grouped_discrete = group.groupby(discrete)
                                                
                        values = [ g.values for n, g in grouped_discrete[a] ]
                        
                        if len(values) == 2:
                            
                            # Mask out the not a numbers
                            values[0] = [ x for x in values[0] if not np.isnan(x) ]
                            values[1] = [ x for x in values[1] if not np.isnan(x) ]
                    
                            # Conduct test for equal variance
                            key = '_'.join([group_var, str(name), discrete, a, 'eqvar'])
                            stats_dict[key] = bartlett(values[0], values[1])
                            
                            # Conduct test for normality
                            key = '_'.join([group_var, str(name), discrete, a, 'normal'])
                            stats_dict[key] = normaltest(np.hstack([values[0], values[1]]))
                            
                            # When you test for equal means (ttest) you have different options
                            # depending on if you have equal variances or not. You can also
                            # run the non-parametric Mann Whitney U test
                            
                            # All three will be entered in the stats_dict
                            
                            # Conduct Welch's t-test (unequal variances)
                            key = '_'.join([group_var, str(name), discrete, a, 'ttest_uneqvar'])
                            stats_dict[key] = ttest_ind(values[1], values[0], equal_var = False)
                        
                            # Conduct standard student's t-test (equal variances)
                            key = '_'.join([group_var, str(name), discrete, a, 'ttest_eqvar'])
                            stats_dict[key] = ttest_ind(values[1], values[0], equal_var = True)
            
                            # Conduct mann whitney U test (non-parametric test of medians)
                            # NOTE that this returns a 1 tailed p value so we multiply it here
                            
                            key = '_'.join([group_var, str(name), discrete, a, 'mannwhitneyu'])
                            u, p = mannwhitneyu(values[1], values[0])
                            stats_dict[key] = (u, p*2)

        # For combos of discrete measures then you can conduct
        # FISHER EXACT tests
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