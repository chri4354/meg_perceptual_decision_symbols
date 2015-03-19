import mne
import numpy as np
import matplotlib.pyplot as plt
from ambiguity.conditions import _combine_events, extract_events
fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject10_cs/run_05_filt-0-30_sss_raw.fif'
# fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject10_cs/run_08_filt-0-30_sss_raw.fif'
# fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject10_cs/run_10_filt-0-30_sss_raw.fif'

# fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject16_mc/run_03_filt-0-30_sss_raw.fif'
# fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject16_mc/run_05_filt-0-30_sss_raw.fif'

extract_events(fname, offset_to_zero_M=True, offset_to_zero_S=False)

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
# plt.plot(_data[:,150000:200000:10].transpose())
# plt.show()

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

# OR manual
first_sample = 0
overlapping = True
data = data[0:len(S_ch),:]
# data = data[len(S_ch):,:]

 #_combine_events function
n_chan, n_sample = data.shape
cmb = np.zeros([n_chan, n_sample])
for bit in range(0, n_chan):
    cmb[bit, :] = 2 ** bit * data[bit, :]
cmb = np.sum(cmb, axis=0)

if not overlapping:
    over_t = np.where(np.sum(data, axis=0) > 1.0)[0]
    cmb[over_t] = 0.0

# Find trigger onsets and offsets
diff = cmb[1:] - cmb[0:-1]
diff[:first_sample] = 0  # don't consider triggers before this
onset = np.where(diff > 0)[0] + 1
offset = np.where(diff < 0)[0]

# minimum changing time
onset_t = np.where((onset[1:] - onset[:-1]) >= min_sample)[0]
onset = onset[np.append(onset_t, len(onset_t))]
offset_t = np.where((offset[1:] - offset[:-1]) >= min_sample)[0] + 1
offset = offset[np.append(0, offset_t)]

# first offsets should be after first onset
if offset[0] < onset[0]:
    offset = offset[1:]
# offsets must go back to 0
if offset_to_zero:
    offset = offset[np.where(cmb[offset+1] == 0.)[0]]
# XXX should do the same for onset?:
# onset = onset[np.where(cmb[onset-1] == 0.)[0]]
if len(onset) > len(offset):
    #onset = onset[:-1]
    offset = np.hstack((offset, onset[-1] + min_sample))
    warnings.warn("Added extra offset!")

# Remove too short samples
duration = offset - onset
sample = onset[duration > min_sample].tolist()
