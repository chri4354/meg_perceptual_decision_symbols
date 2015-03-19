import mne
import numpy as np
import matplotlib.pyplot as plt
from ambiguity.conditions import _combine_events
fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject06_ha/run_10_filt-0-30_sss_raw.fif'
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

# Min duration in sample
min_sample = min_duration * raw.info['sfreq']

# Binarize trigger values from 5 mV to 0 and 1
S_ch = range(0, 11)
M_ch = range(11, n_bits)

# from function
start = 140000
cmb_M, sample_M = _combine_events(data[len(S_ch):,:], min_sample, start)
cmb_S, sample_S = _combine_events(data[0:len(S_ch),:], min_sample, sample_M[0])

# OR manual
data = data[len(S_ch):,:]
n_chan, n_sample = data.shape
cmb = np.zeros([n_chan, n_sample])
for bit in range(0, n_chan):
    cmb[bit, :] = 2 ** bit * data[bit, :]
cmb = np.sum(cmb, axis=0)

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

# Correct inequality of triggers' onsets and offsets
if offset[0] < onset[0]:
    offset = offset[1:]
if len(onset) > len(offset):
    #onset = onset[:-1]
    offset = np.hstack((offset, onset[-1] + min_sample))
    warnings.warn("Added extra offset!")

# Remove too short samples
duration = offset - onset
sample = onset[duration > min_sample].tolist()
