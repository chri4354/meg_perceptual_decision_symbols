import mne
import numpy as np
import scipy.io as sio
import os.path as op

from toolbox.jr_toolbox import struct

data_path = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/'
fname_epochs = 'MEG/subject05_cl/stim-subject05_cl-epo.fif'
fname_bhv = 'behavioral/cl_behaviorMEG.mat'

# Read Mat file
fname = op.join(data_path,fname_bhv)
trials = sio.loadmat(fname, squeeze_me=True, struct_as_record=True)["trials"]

# keys = ['type', 'target_code', 'target', 'amb', 'side', 'respond', 'feedback',
#         'key', 'timeout', 'keycode', 'correct', 'RT', 'soft_correct',
#         'amb_word', 'choice', 'choice_bar', 'RT_MEG']

keys = [('side', 'stim_side', int),
        ('amb', 'stim_contrast', float),
        ('amb_word', 'stim_letter', float),
        ('respond', 'bhv', bool),
        ('key', 'bhv_side', int),
        ('correct', 'bhv_correct', float),
        ('RT_MEG', 'bhv_RT', float),
        ('choice', 'bhv_category', int),
        ('choice_bar', 'bhv_contrast', float)]
events = list()
for trial in trials:
    event = dict()
    for key in keys:
        event[key[1]] = trial[key[0]]
    event['trigger_value'] = int(trial['ttl']['value'])
    events.append(event)

events = struct(events)

fname = op.join(data_path,fname_epochs)
epochs = mne.read_epochs(fname)

np.all(epochs.events[:,2] == events.get('trigger_value'))
