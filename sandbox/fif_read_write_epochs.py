import mne
import numpy as np
from mne.preprocessing import read_ica
from ambiguity.conditions import events_select_condition

data_path = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/'
raw_fname = 'subject05_cl/run_01_filt-1-40_sss_raw.fif'
eve_fname = 'subject05_cl/run_01_filt-1-40_sss-eve.fif'
ica_fname = 'subject05_cl/mag-ica.fif'
save_fname = 'subject05_cl/test-epo.fif'
raw = mne.io.Raw(data_path+raw_fname)

events = mne.read_events(data_path+eve_fname)

sel = events_select_condition(events[:,2], 'motor')
events_sel = events[sel,:]

# Epoch raw data
epochs = mne.Epochs(raw=raw, preload=True, event_id=None, events=events_sel,
                    reject=dict(grad=4000e-12, mag=4e-11, eog=180e-5),
                    decim=3, tmin=-1.800, tmax=0.5, baseline=None)

# Redefine t0 if necessary
epochs.times += -0.410
epochs.tmin += -0.410
epochs.tmax += -0.410

# ICA correction
ica = read_ica(data_path + ica_fname)
ica.apply(epochs)

# Save
epochs.save(data_path + save_fname)

# Read
epochs = mne.read_epochs(data_path + save_fname)
