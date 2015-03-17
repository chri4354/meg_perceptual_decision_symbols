# check events
import sys
import os.path as op
import numpy as np
import mne

from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from ambiguity.conditions import events_select_condition

from collections import Counter
from scripts.config import (
    data_path,
    subjects,
    runs,
    results_dir,
    raw_fname_filt_tmp,
    events_fname_filt_tmp,
)

this_path = op.join(data_path, 'MEG', 'subject05_cl')

for r in runs:
    e = mne.read_events(op.join(this_path, events_fname_filt_tmp.format(r)))
    if r == 1:
        events = e[:,2]
    else:
        events = np.append(events, e[:,2], axis=0)
print(Counter(events))
print(sum(events<64))


## Check whether triggers are aligned to epochs
import matplotlib.pyplot as plt
import mne
import numpy as np
data_path = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/'
fname = 'subject05_cl/stim-subject05_cl-epo.fif'
epochs = mne.read_epochs(data_path+fname)
x=epochs._data[:,-3,:]
plt.imshow(x)
plt.show()
