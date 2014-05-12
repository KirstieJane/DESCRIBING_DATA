#!/usr/bin/env python

def make_table_group_compare(df, group_var, stats_dict, group_names_long, continuous_measures=None, discrete_measures=None):
    
    # We're going to make a nice list of text strings
    # that we'll eventually write to a text file
    
    # Import what you need
    import numpy as np

    # Create an empty list
    table_list = list()
    
    # By default our symbol for the statistics will be '='
    symbol = '='
    
    # I don't think we need this empty row any more....
    # but let's just see, shall we...
    empty_row = [''] * 4
    
    # Read the number of participants in each group for the first 
    # continuous measure and the first discrete measures
    if continuous_measures:
        (n0_all, n1_all) = ( stats_dict['_'.join([continuous_measures[0], 'n'])] )
    elif discrete_measures:
        (n0_all, n1_all) = ( stats_dict['_'.join([discrete_measures[0][0], 'n'])] )
    
    # Create the first row of text
    # which contains the names of the groups
    # and the number of participants in each
    row_text = ['', '{} Cohort n={:2.0f}'.format(group_names_long[1], n1_all),
                            '{} Cohort n={:2.0f}'.format(group_names_long[0], n0_all),
                            'Test {} <> {}'.format(group_names_long[1], group_names_long[0])]
                            
    # Add this row of text to the table_list appended by a tab
    table_list.append('\t'.join(row_text))
    
    # For all the discrete measures...
    if discrete_measures:
        
        # Find the measure name and the labels from the discrete_measures list
        for measure, labels in zip(discrete_measures[0], discrete_measures[1]):
            
            # Group the data by the group_variable and the discrete measure
            grouped_again = df.groupby([group_var, measure])
            
            # If there are values in all four cells then report 
            # the fisher's exact test
            if len(np.array(grouped_again[measure].count())) == 4:

                (n0_0, n0_1, n1_0, n1_1), (odr, p ) = ( stats_dict['_'.join([group_var, measure, 'n'])][:],
                                                        stats_dict['_'.join([group_var, measure, 'fisher'])] )
                
                # We know that the symbol is usually '='
                # but if the p value is very small then we'll
                # change that symbol to '<' and the p value to 0.001
                symbol = '='
                if p < 0.001:
                    symbol, p = '<', 0.001
                
                # Now figure out the next row of text
                # it starts with the measure, and then contains
                # the numbers for each group, and finally
                # the odds ratio and pvalue

                # If there are missing data points we'd like to report
                # those in the table
                if (n0_all + n1_all) <> (n0_0 + n0_1 + n1_0 + n1_1):
                    row_text = [ measure, '{:1.0f} {} vs {:1.0f} {}, {} missing'.format(n1_0, labels[0], n1_1, labels[1], (n1_all - n1_0 - n1_1)),
                                      '{:1.0f} {} vs {:1.0f} {}, {} missing'.format(n0_0, labels[0], n0_1, labels[1], (n0_all - n0_0 - n0_1)),
                                      'or = {:2.2f}, p {} {:1.3f}'.format( odr, symbol, p ) ]                    
                else:
                    row_text = [ measure, '{:1.0f} {} vs {:1.0f} {}'.format(n1_0, labels[0], n1_1, labels[1]),
                                      '{:1.0f} {} vs {:1.0f} {}'.format(n0_0, labels[0], n0_1, labels[1]),
                                      'or = {:2.2f}, p {} {:1.3f}'.format( odr, symbol, p ) ]

                # Add this row_text to the table_list                
                table_list.append('\t'.join(row_text))

    if continuous_measures:
        for measure in continuous_measures:
            # Read in a bunch of measures from the stats_dict
            (mean1, mean0) = stats_dict['_'.join([measure, 'mean'])]
            (std1, std0) = stats_dict['_'.join([measure, 'std'])]
            (perc25_1, perc25_0) = stats_dict['_'.join([measure, 'perc25'])]
            (perc50_1, perc50_0) = stats_dict['_'.join([measure, 'perc50'])]
            (perc75_1, perc75_0) = stats_dict['_'.join([measure, 'perc75'])]
            (n0, n1) = stats_dict['_'.join([measure, 'n'])]
            (var_t, var_p) = stats_dict['_'.join([measure, 'eqvar'])]
            (mean_teq, mean_peq) = stats_dict['_'.join([measure, 'ttest_eqvar'])]
            (mean_tuneq, mean_puneq) = stats_dict['_'.join([measure, 'ttest_uneqvar'])]
            (mannwhitney_u, mannwhitney_p) = stats_dict['_'.join([measure, 'mannwhitneyu'])]
            (normal_k, normal_p) = stats_dict['_'.join([measure, 'normal'])] 
            
            # You can conduct a t-test if the data is normally distributed
            if normal_p > 0.05:
                # The degrees of freedom for an independent t-test is
                # n1 + n2 -2
                df = n0 + n1 - 2
                
                # If the variances are equal then we can use the eqvar t-test
                if var_p > 0.05:
                    test_stat = mean_teq
                    test_p = mean_peq
                    
                    uneq_var_text = ''
                
                else:
                    test_stat = mean_tuneq
                    test_p = mean_puneq
                    
                    symbol = '='
                    if var_p < 0.001:
                        symbol, var_p = '<', 0.001

                    uneq_var_text = '(Unequal Variance, p {} {:2.3f})'.format(symbol, var_p)

                # Adjust the symbol if the test is very significant
                symbol = '='
                if test_p < 0.001:
                    symbol, test_p = '<', 0.001
        
                # Make sure to report if there are any missing data points
                if (n0 != n0_all or n1 != n1_all):
                    row_text = [ measure, '{:2.3g} ({:2.3g}), {} missing'.format(mean0, std0, (n0_all - n0)),
                                    '{:2.3g} ({:2.3g}), {} missing'.format(mean1, std1, (n1_all - n1)),
                                    't({:1.0f}) = {:2.3g}, p {} {:2.3g} {}'.format(df,np.float(test_stat), symbol, test_p, uneq_var_text)]

                else:
                    row_text = [ measure, '{:2.3g} ({:2.3g})'.format(mean0, std0),
                                    '{:2.3g} ({:2.3g})'.format(mean1, std1),
                                    't({:1.0f}) = {:2.3g}, p {} {:2.3g} {}'.format(df,np.float(test_stat), symbol, test_p, uneq_var_text)]
            
            else:
                # If you don't have normally distributed data then you need
                # to use a mann whitney U test
                test_stat = mannwhitney_u
                test_p = mannwhitney_p
                print mannwhitney_p
                
                # Adjust the symbol if the test of non-normality is very significant
                symbol = '='
                if normal_p < 0.001:
                    symbol, normal_p = '<', 0.001
    
                normal_dist_text = '(Test of normality failed, p {} {:2.3f})'.format(symbol, normal_p)
                
                # Adjust the symbol if the test is very significant
                symbol = '='
                if test_p < 0.001:
                    symbol, test_p = '<', 0.001
                    
                # Make sure to report if there are any missing data points
                if (n0 != n0_all or n1 != n1_all):
    
                    row_text = [ measure, '{:2.3g} ({:2.3g}-{:2.3g}), {} missing'.format(perc50_0, perc25_0, perc75_0, (n0_all - n0)),
                                    '{:2.3g} ({:2.3g}-{:2.3g}), {} missing'.format(perc50_1, perc25_1, perc75_1, (n1_all - n1)),
                                    'U = {:2.3g}, p {} {:2.3g} {}'.format(np.float(test_stat), symbol, test_p, normal_dist_text)]
                else:
                    row_text = [ measure, '{:2.3g} ({:2.3g}-{:2.3g})'.format(perc50_0, perc25_0, perc75_0),
                                    '{:2.3g} ({:2.3g}-{:2.3g})'.format(perc50_1, perc25_1, perc75_1),
                                    'U = {:2.3g}, p {} {:2.3g} {}'.format(np.float(test_stat), symbol, test_p, normal_dist_text)]

            # Now add this to your table_list            
            table_list.append('\t'.join(row_text)) 

    return table_list
    