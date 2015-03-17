import mne
import numpy as np
data_path = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/'
fname = 'subject05_cl/stim-subject05_cl-epo.fif'
# fname = 'subject01_ar/stim-subject01_ar-epo.fif'
# fname = 'subject02_as/stim-subject02_as-epo.fif'
epochs = mne.read_epochs(data_path+fname)

evoked = epochs.average()
evoked.plot()
times = np.arange(0.05, 0.15, 0.01)
evoked.plot_topomap(times, ch_type='mag')

left = np.where(epochs.events[:,2] % 2)[0]
right = np.where((epochs.events[:,2] + 1) % 2)[0]
evoked_left = epochs[left].average()
evoked_right = epochs[right].average()
evoked_left.comment = 'left'
evoked_right.comment = 'right'
contrast = evoked_left - evoked_right
contrast.plot()
times = np.arange(0.05, 0.250, 0.010)
contrast.plot_topomap(times, ch_type='mag')



import mne
import numpy as np
data_path = '/media/harddrive/2013_meg_ambiguity/python/'
fname = 'data/ambiguity/MEG/subject05_cl/stim-subject05_cl-epo.fif'
epochs = mne.read_epochs(data_path+fname)
left = np.where(epochs.events[:,2] % 2)[0]
right = np.where((epochs.events[:,2] + 1) % 2)[0]
evoked_left = epochs[left].average()
evoked_right = epochs[right].average()
contrast = evoked_left - evoked_right
