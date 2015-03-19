import mne
import numpy as np
import matplotlib.pyplot as plt
from ambiguity.conditions import _combine_events, extract_events, get_events
fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject17_az/run_02_sss.fif'
raw = mne.io.Raw(fname, preload=True)
