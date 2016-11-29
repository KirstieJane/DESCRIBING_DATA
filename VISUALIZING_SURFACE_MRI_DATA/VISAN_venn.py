#!/usr/bin/env python

import numpy as np
import matplotlib.pylab as plt
from matplotlib_venn import venn3
import seaborn as sns
sns.set_style('white')
sns.set_context('poster', fontscale=2)
'''
Colors are in the following order:
  * Cope 1 only - yellow
  * Cope 2 only - orange
  * Cope 1 and 2 - red
  * Cope 4 only - purple
  * Cope 1 and 4 - Blue
  * Cope 2 and 4 - Green
  * Cope 1, 2, 4 - Pink
'''    
cmap = [ (255/255.0, 255/255.0,  51/255.0),
         (255/255.0, 127/255.0,   0/255.0),
         (228/255.0,  26/255.0,  28/255.0),
         (152/255.0,  78/255.0, 163/255.0),
         ( 55/255.0, 126/255.0,  184/255.0),
         ( 77/255.0, 175/255.0,  74/255.0),
         (247/255.0, 129/255.0, 191/255.0) ]

venn_dict = { 1 : '100',
              2 : '010',
              3 : '110',
              4 : '001',
              5 : '101',
              6 : '011',
              7 : '111' }
         
     
fig, ax = plt.subplots(figsize=(10,10))
         
v = venn3(subsets=(3,3,3,3,3,3,1),
          set_labels = ('semantic        \n> baseline', 
                        'analogy         \n> baseline',
                        'analogy > semantic'),
          ax=ax)

for i in range(7):
    id = venn_dict[i+1]
    v.get_patch_by_id(id).set_color(cmap[i])
    v.get_patch_by_id(id).set_alpha(1.0)

[ x.set_text('') for x in v.subset_labels ]

[ x.set_fontsize(25) for x in v.set_labels ]

v.set_labels[0].set_position((-0.36, 0.2))
v.set_labels[0].set_horizontalalignment("center")
v.set_labels[1].set_position((0.42, 0.2))
v.set_labels[1].set_horizontalalignment("center")
v.set_labels[2].set_position((0.0, -0.42))

fig.savefig('C:\Users\Kirstie\Dropbox\KW_NORA\VISAN\Shared_VisAn_Manuscript_Frontiers\TESTING.png', dpi=150, bbox=0)
plt.show()
