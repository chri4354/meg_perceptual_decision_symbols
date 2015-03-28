import mne
import numpy as np
data_path = "/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject05_cl/"
fname = 'run_03_sss.fif'
raw = mne.io.Raw(data_path+fname, preload=True)

S_ch = ['STI001', 'STI002', 'STI003', 'STI004', 'STI005', 'STI006']
M_ch = ['STI013', 'STI015']
raw.pick_channels(S_ch + M_ch)

events = mne.find_events(raw, stim_channel='STI101', consecutive='increasing',
                        min_duration=0.000, verbose=True)
