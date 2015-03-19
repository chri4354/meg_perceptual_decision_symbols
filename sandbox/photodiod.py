'''this scripts aims at finding the delay introduced by the trigger jitter +
 intrisic delay + filter through the photodiod'''

import mne
import numpy as np
from ambiguity.conditions import events_select_condition, get_events
import matplotlib.pyplot as plt
raw_fname = 'data/ambiguity/MEG/subject15_tb/run_01_filt-0-30_sss_raw.fif'
eve_fname = 'data/ambiguity/MEG/subject15_tb/run_01_filt-0-30_sss-eve.fif'

raw_fname = 'data/ambiguity/MEG/subject14_ap/run_01_filt-0-30_sss_raw.fif'
eve_fname = 'data/ambiguity/MEG/subject14_ap/run_01_filt-0-30_sss-eve.fif'

events = mne.read_events(eve_fname)
events = events[events[:,2]<4096, :]

raw = mne.io.Raw(raw_fname, preload=False)
picks = mne.pick_types(raw.info, meg=False, eeg=False, eog=False, stim=True,
                       misc=True)
epochs = mne.Epochs(raw=raw, event_id=None, picks=picks, preload=True, events=events,
                    tmin=0.300, tmax=.500, decim=4, baseline=[0.300, 0.400])

# normalize
if False:
    for ch in range(len(epochs.ch_names)):
        for ep in range(len(epochs)):
            epochs._data[ep,ch,:] -= np.min(epochs._data[ep,ch,:])
            epochs._data[ep,ch,:] /= (np.max(epochs._data[ep,ch,:]) -
                                      np.min(epochs._data[ep,ch,:]))

    fig, axs = plt.subplots(5, 7, sharey=True)
    axs = axs.reshape((35,))
    for ii in range(len(epochs.ch_names)):
        axs[ii].imshow(epochs._data[:,ii,:])
        axs[ii].set_title(epochs.ch_names[ii])
    plt.show()



ch = np.where(np.array(epochs.ch_names) == 'MISC004')[0][0]
mne.viz.plot_image_epochs(epochs, ch, scalings=dict(stim=1e10), units=dict(stim=''))

epochs.times[np.where(np.mean(epochs._data[:,ch,:], axis=0) > 0.08)[0][0]]
