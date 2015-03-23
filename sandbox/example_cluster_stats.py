import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mne.viz import plot_topomap

import mne
from mne.stats import spatio_temporal_cluster_test
from mne.datasets import sample
from mne.channels import read_ch_connectivity

from toolbox.utils import cluster_stat

print(__doc__)

###############################################################################

# Set parameters
data_path = sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'
event_id = {'Aud_L': 1, 'Aud_R': 2, 'Vis_L': 3, 'Vis_R': 4}
tmin = -0.2
tmax = 0.5

# Setup for reading the raw data
raw = mne.io.Raw(raw_fname, preload=True)
raw.filter(1, 30)
events = mne.read_events(event_fname)

###############################################################################
# Read epochs for the channel of interest

picks = mne.pick_types(raw.info, meg='mag', eog=True)

reject = dict(mag=4e-12, eog=150e-6)
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, picks=picks,
                    baseline=None, reject=reject, preload=True)

picks = [epochs.ch_names[ii] for ii in mne.pick_types(epochs.info, meg='mag')]
epochs.pick_channels(picks)
epochs.equalize_event_counts(event_id, copy=False)

epochsList = [epochs[('Aud_L', 'Aud_R')], epochs[('Vis_L', 'Vis_R')]]
cluster = cluster_stat(epochsList, n_permutations=2 ** 11,
                       threshold=dict(start=1., step=1.), n_jobs=-1)

# Plots
i_clus = np.where(cluster.p_values_ < .001)
cluster.plot(i_clus=i_clus)
cluster.plot_topomap(sensors=False, contours=False, show=True)
