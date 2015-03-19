import mne
import numpy as np
from toolbox.jr_toolbox import my_resample
from scipy.signal import resample
import numpy as np

epo_fname = 'data/ambiguity/MEG/subject05_cl/stim_lock-subject05_cl-epo.fif'
epochs = mne.read_epochs(epo_fname)

print(np.shape(epochs._data))
epochs = my_resample(epochs, epochs.info['sfreq'] / 2)
print(np.shape(epochs._data))
