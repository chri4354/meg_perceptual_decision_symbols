from scripts.config import get_events
import matplotlib.pyplot as plt
eventsM = get_events('data/ambiguity/behavior/rm_behaviorMEG.mat', 'motor_lock')
events = get_events('data/ambiguity/behavior/rm_behaviorMEG.mat')

np.where((mat[0:1587] - fiff) != 0)[0][0]
eventsM['trial_number'][202]


raw = mne.io.Raw('/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject03_rm/run_02_filt-0-30_sss_raw.fif', preload=False)

events = mne.read_events('/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject03_rm/run_02_filt-0-30_sss-eve.fif')

rt = list()
for ii in range(0, len(events)):
    if (events[ii, 2] <= 4.0 and events[ii + 1, 2] > 4000):
        rt.append((events[ii+1, 0] - events[ii, 0]) / raw.info['sfreq'])


import mne
import numpy as np
import matplotlib.pyplot as plt
raw = mne.io.Raw('/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject03_rm/run_02_filt-0-30_sss_raw.fif', preload=True)
raw.pick_channels(['STI101'])

plt.plot(np.log(1.+np.transpose(raw._data[0,60000:80000])))
plt.show()
