#!/usr/bin/env python

def make_table_group_compare(df, group_var, stats_dict, group_names_long, continuous_measures=None, discrete_measures=None):
    
    # We're going to make a pretty table
    import prettytable as pt
    import pandas as pd
    import numpy as np

    # Group the data by the group variable
    grouped = df.groupby(group_var)

    table_list = list()
    
    symbol = '='

    if continuous_measures:
        (n0_all, n1_all) = ( stats_dict['_'.join([continuous_measures[0], 'n'])] )
    elif discrete_measures:
        (n0_all, n1_all) = ( stats_dict['_'.join([discrete_measures[0][0], 'n'])] )
    
    row_text = ['', '{} Cohort n={:2.0f}'.format(group_names_long[1], n1_all),
                            '{} Cohort n={:2.0f}'.format(group_names_long[0], n0_all),
                            'Test of means {} <> {}'.format(group_names_long[1], group_names_long[0])]
    x = pt.PrettyTable(row_text)
    table_list.append('\t'.join(row_text))
    
    empty_row = [''] * 4
    
    if discrete_measures:
        for measure, labels in zip(discrete_measures[0], discrete_measures[1]):
            grouped_again = df.groupby([group_var, measure])
            
            if len(np.array(grouped_again[measure].count())) == 4:

                (n0_0, n0_1, n1_0, n1_1), (odr, p ) = ( stats_dict['_'.join([group_var, measure, 'n'])][:],
                                                        stats_dict['_'.join([group_var, measure, 'fisher'])] )
                
                symbol = '='
                if p < 0.001:
                    symbol, p = '<', 0.001
                
                row_text = [ measure, '{:1.0f} {} vs {:1.0f} {}'.format(n1_0, labels[0], n1_1, labels[1]),
                                      '{:1.0f} {} vs {:1.0f} {}'.format(n0_0, labels[0], n0_1, labels[1]),
                                      'or = {:2.2f}, p {} {:1.3f}'.format( odr, symbol, p ) ]
                x.add_row(row_text)
                table_list.append('\t'.join(row_text))

                if (n0_all + n1_all) <> (n0_0 + n0_1 + n1_0 + n1_1):
                    row_text = [ '','{} missing'.format((n1_all - n1_0 - n1_1)),'{} missing'.format((n0_all - n0_0 - n0_1)),'']

                    x.add_row(row_text)
                    
                    table_list.append('\t'.join(row_text))
                x.add_row(empty_row)

    if continuous_measures:
        for measure in continuous_measures:
            ((mean1, mean0), (std1, std0),
                (n0, n1), (mean_t, mean_p),
                (var_t, var_p) ) = ( stats_dict['_'.join([measure, 'mean'])],
                                                stats_dict['_'.join([measure, 'std'])],
                                                stats_dict['_'.join([measure, 'n'])],
                                                stats_dict['_'.join([measure, 'eq_means'])],
                                                stats_dict['_'.join([measure, 'eq_var'])] )
    
            df = n0 + n1 - 2
            symbol = '='
            if mean_p < 0.001:
                symbol, mean_p = '<', 0.001
            row_text = [ measure, '{:2.3g} ({:2.3g})'.format(mean0, std0),
                                '{:2.3g} ({:2.3g})'.format(mean1, std1),
                                't({:1.0f}) = {:2.3g}, p {} {:2.3g}'.format(df,np.float(mean_t), symbol, mean_p)]
            x.add_row(row_text)
            table_list.append('\t'.join(row_text)) 

            symbol = '='
            if var_p < 0.05:
                if var_p < 0.001:
                    symbol, var_p = '<', 0.001
                uneq_var_text = ['(Unequal Variance, p {} {:2.3f})'.format(symbol, var_p)]
            else:
                uneq_var_text = ['']
                
            if (n0 != n0_all or n1 != n1_all):
                missing_text = [ 'missing: {}'.format((n1_all - n1)),'missing: {}'.format((n0_all - n0)) ]
            else:
                missing_text = ['','']
                
            if var_p < 0.05 or n0 != n0_all or n1 != n1_all:
                row_text = [ '',missing_text[0], missing_text[1], uneq_var_text[0]]
                x.add_row([ '',missing_text[0], missing_text[1], uneq_var_text[0]])
                table_list.append('\t'.join(row_text)) 

            x.add_row(empty_row)
       
    return x, table_list
    