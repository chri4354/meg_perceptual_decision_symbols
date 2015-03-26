import mne
import numpy as np
data_path = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/'
fname = 'subject01_ar/stim-subject01_ar-epo.fif'
fname = 'subject01_ar/stim_lock-subject01_ar-epo.fif'
epochs = mne.read_epochs(data_path+fname)
# epochs = epochs[range(10)]
# epochs.save(data_path+'subject01_ar/stim-subject01_ar_0-10-epo.fif')


cov = mne.compute_covariance(epochs , method='shrunk')
evoked = epochs.average()
evoked.plot_white(cov)
