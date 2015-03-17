import numpy as np
import mne
import matplotlib.pyplot as plt
datapath = '/media/harddrive/2013_meg_ambiguity/matlab/data/sss/'
file = 'cl120289_main_1_sss.fif'
raw = mne.io.Raw(datapath+file, preload=True)
raw.plot()
mag_picks = mne.pick_types(raw.info, meg='mag', eeg=False, exclude='bads')
ecg_surrogate = raw[mag_picks,:][0].mean(axis=0)
ecg_pick = mne.pick_types(raw.info, meg=False, ecg=True)
raw._data[ecg_pick,:] = ecg_surrogate * 1e10
raw.plot()
