import numpy as np
import nibabel as nib
import matplotlib.pylab as plt

cope_file = 'MD_500_glm_cope_tstat2.nii.gz'
tstat_file = 'MD_500_tstat2.nii.gz'
p_file = 'MD_500_tfce_corrp_tstat2.nii.gz'

cope = nib.load(cope_file)
cope_data = cope.get_data()
tstat = nib.load(tstat_file)
tstat_data = tstat.get_data()
p = nib.load(p_file)
p_data = p.get_data()

m_tstat = np.ma.masked_values(tstat_data, 0)
