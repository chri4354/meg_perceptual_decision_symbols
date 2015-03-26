import numpy as np
import matplotlib.pyplot as plt
import pickle
import mne
import sys

fname = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject01_ar/motor_lock-subject01_ar-decod_stim_category_motor_right.pickle'
with open(fname) as f:
    gat, contrast = pickle.load(f)

down = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/subject01_ar/test.pickle'
with open(down, 'w') as f:
    x = gat.estimators_[0][0]
    x = gat.estimators_[0][0].steps[1].__getitem__(1).coef_
    pickle.dump(x, f)
