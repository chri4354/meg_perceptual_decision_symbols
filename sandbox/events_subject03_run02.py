import mne
import numpy as np
import matplotlib.pyplot as plt
from ambiguity.conditions import _combine_events, extract_events, get_events
fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject03_rm/run_02_filt-0-30_sss_raw.fif'
bhv_fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/behavior/rm_behaviorMEG.mat'

all_events = get_events(bhv_fname)
mat_events = get_events(bhv_fname, 'motor_lock')
events = extract_events(fname) # , offset_to_zero_M=True, offset_to_zero_S=False

raw = mne.io.Raw(fname, preload=True)

# Dissociate STI101 into distinct channels
min_duration = 0.003
raw.pick_channels(['STI101'])
n_bits = 16
raw._data = np.round(raw._data)
data = np.zeros((n_bits, raw.n_times))
for bit in range(0, n_bits)[::-1]:
    data[bit, :] = (raw._data >= 2 ** bit).astype(float)
    raw._data -= data[bit, :] * (2 ** bit)

_data = np.copy(data)
for l in range(data.shape[0]):
    _data[l,:] = _data[l,:] + l * 1.1

eventsS = events[events[:,2]< 4000,:]
eventsM = events[events[:,2]> 4000,:]
plt.plot(_data[:,145000:165000].transpose())
plt.show()

r = np.arange(-5,5)
plt.plot(np.array(mat_events['motor_side'][r + 202].astype(list)))
index= np.where(eventsM[:,0]>eventsS[51, 0])[0][0]
plt.plot(eventsM[r + index, 2]>16000)
plt.show()

# Min duration in sample
min_sample = min_duration * raw.info['sfreq']

# Binarize trigger values from 5 mV to 0 and 1
S_ch = range(0, 11)
M_ch = range(11, n_bits)

# from function
first_sample = 0
offset_to_zero = False
cmb_M, sample_M = _combine_events(data[len(S_ch):,:], min_sample,
                                  first_sample=first_sample,
                                  overlapping=False,
                                  offset_to_zero=offset_to_zero)
# Only consider stim triggers after first button response (to avoid trigger
# test trhat shouldn't have been recorded)
cmb_S, sample_S = _combine_events(data[0:len(S_ch),:], min_sample,
                                  first_sample=sample_M[0],
                                  overlapping=True,
                                  offset_to_zero=offset_to_zero)
