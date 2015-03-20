import os.path as op
import numpy as np
import matplotlib.pyplot as plt

from toolbox.utils import cluster_stat

import mne

from scripts.config import (
    data_path,
    subjects,
    results_dir,
    epochs_params,
    open_browser,
    contrasts,
)


# Apply contrast on each type of epoch
# for ep in epochs_params:
#     for contrast in contrasts[0]:
ep = epochs_params[0]
contrast = contrasts[0]
evokeds = ([], [])
for s, subject in enumerate(subjects):
    ave_fname = op.join(data_path, 'MEG', subject,
                        '{}-{}-contrasts-ave.fif'.format(ep['name'],
                                                         subject))
    for v, value in enumerate(contrast['include']['values']):
        evoked = mne.read_evokeds(ave_fname, contrast['name']+str(value))
        picks = [evoked.ch_names[ii] for ii in mne.pick_types(evoked.info, meg='mag')]
        evoked.pick_channels(picks)
        evokeds[v].append(evoked)


pos = mne.find_layout(evoked.info).pos


stats = cluster_stat(evokeds, pos=pos)
# figs = stats.plot_cluster_topo()
# figs = stats.plot_cluster_time()
# figs = stats.plot()
figs = stats.plot_evoked_time()
