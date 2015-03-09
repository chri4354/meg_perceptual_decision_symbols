import numpy as np
import scipy.io as sio
import mne
from mne.io.meas_info import create_info
from mne.epochs import EpochsArray

# change this path accordingly
filename = '/media/DATA/Pro/Projects/Paris/Categorization/MEG_StringsNumbers/data/preprocessed/ar_concatenated.mat'

# --------------------------------------------------------------
# PREPROCESS DATA
# --------------------------------------------------------------
# load Matlab-Fieldtrip data
import h5py
mat = h5py.File(filename, squeeze_me=True, struct_as_record=False)
#mat = sio.loadmat(filename, squeeze_me=True, struct_as_record=False)
ft_data = mat['data_concatenated']

# Concert fieldtrip data to MNE-Python (I will make a cleaner function 
# when I come back)
n_trial = len(ft_data['trial'])
n_chans, n_time = mat[ft_data['trial'][0][0]].shape
data = np.zeros((n_trial, n_chans, n_time))
for trial in range(n_trial):
  data[trial, :, :] = mat[ft_data['trial'][trial][0]].value
sfreq = float(ft_data['fsample'].value[0][0]) # sampling frequency
time = mat[ft_data['time'][0][0]].value
tmin = min(time)
chan_names = [l.encode('ascii') for l in ft_data['label']]
chan_names = [u''.join(unichr(c) for c in label) for label in mat[ft_data['label'][0][label]].value)

chan_types = ft_data.label
chan_types[0:305:3] = 'grad'
chan_types[1:305:3] = 'grad'
chan_types[2:306:3] = 'mag'
chan_types[307:] = 'misc'

info = create_info(chan_names, sfreq, chan_types)
# define MNE-events: it can only take one category of events so we'll go over it afterwards
events = np.c_[np.cumsum(np.ones(n_trial)) * 5 * sfreq, # start sample in raw data
			   np.zeros(n_trial), 
               ft_data.trialinfo]  # can only take one category of events
epochs = EpochsArray(data, info, events=events, tmin=tmin)