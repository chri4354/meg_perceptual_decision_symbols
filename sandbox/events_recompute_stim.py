import sys
import mkl
import os.path as op

import numpy as np

import mne

from meeg_preprocessing.utils import setup_provenance

from ambiguity.conditions import events_select_condition

from scripts.config import (
    data_path,
    event_id,
    raw_fname_filt_tmp,
)


subject = 'subject05_cl'
r = 1

this_path = op.join(data_path, 'MEG', subject)

fname = op.join(this_path, raw_fname_filt_tmp.format(r))


raw = mne.io.Raw(fname, preload=True)
stim_channels = ['STI001', 'STI002', 'STI003', 'STI004', 'STI005', 'STI006']
raw.pick_channels(stim_channels)

# Binarize trigger values from 5 mV to 0 and 1
raw._data = np.round(raw._data / 5)

# recompute binary triggers
cmb = np.zeros(raw._data.shape)
for bit in range(0, raw._data.shape[0]):
    cmb[bit, :] = 2 ** (bit - 1) * raw._data[bit, :]
cmb = np.sum(surrogate_chan, axis=0)
diff = cmb[0:-1] - cmb[1:]

# find triggers
events = np.where(diff > 0)[0] + 1

# XXX add minimum duration and identify bugs

# create events object
events = np.append(events, np.zeros(events.shape), cmb[events], axis=1)



#############################################
import sys
import mkl
import os.path as op
import numpy as np
import matplotlib.pyplot as plt
import mne

subject = 'subject04_jm'
r = 1
this_path = op.join('/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/', subject)

fname = op.join(this_path, 'run_01_filt-0-30_sss_raw.fif')

stim_channels = ['STI101', 'STI201', 'STI301', 'MISC201', 'MISC202', 'MISC203',
                 'MISC204', 'MISC205', 'MISC206', 'MISC301', 'MISC302',
                 'MISC303', 'MISC304', 'MISC305', 'MISC306']
raw = mne.io.Raw(fname, preload=True)
raw.pick_channels(raw.ch_names[306:])

for ii in range(70, len(raw.ch_names)):
    print(ii)
    plt.plot(raw._data[ii,100000:200000])
    plt.show()

plt.plot(raw._data[73,100000:200000])

d = np.log(raw._data[:,100000:200000])
plt.imshow(d, aspect='auto', interpolation='none')
plt.show()

stim_channels = ['STI001', 'STI002', 'STI003', 'STI004', 'STI005', 'STI006']
raw.pick_channels(stim_channels)

# Binarize trigger values from 5 mV to 0 and 1
raw._data = np.round(raw._data / 5)

# recompute binary triggers
cmb = np.zeros(raw._data.shape)
for bit in range(0, raw._data.shape[0]):
    cmb[bit, :] = 2 ** (bit - 1) * raw._data[bit, :]
cmb = np.sum(surrogate_chan, axis=0)
diff = cmb[0:-1] - cmb[1:]

# find triggers
events = np.where(diff > 0)[0] + 1

# XXX add minimum duration and identify bugs

# create events object
events = np.append(events, np.zeros(events.shape), cmb[events], axis=1)
