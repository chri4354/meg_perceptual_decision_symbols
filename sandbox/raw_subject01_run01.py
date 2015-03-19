import mne
import numpy as np
import matplotlib.pyplot as plt
from ambiguity.conditions import _combine_events, extract_events, get_events
fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject01_ar/run_01_sss.fif'
raw = mne.io.Raw(fname, preload=True)
