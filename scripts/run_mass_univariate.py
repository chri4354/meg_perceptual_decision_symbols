import os.path as op
import numpy as np
import matplotlib.pyplot as plt

from toolbox.utils import cluster_stat, Evokeds_to_Epochs
from meeg_preprocessing.utils import setup_provenance

import mne

from scripts.config import (
    data_path,
    subjects,
    results_dir,
    epochs_params,
    open_browser,
    contrasts,
)


report, run_id, results_dir, logger = setup_provenance(
    script='scripts/run_mass_univariate.py', results_dir=results_dir) # __file__


# Apply contrast on each type of epoch
for ep in epochs_params:
    for contrast in contrasts:
        print(contrast)
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
    
        # Connectivity
        connectivity, ch_names = read_ch_connectivity('neuromag306mag')

        # Stats
        cluster = cluster_stat(evokeds, n_permutations=2 ** 11,
                               connectivity=connectivity,
                               threshold=dict(start=1., step=1.), n_jobs=-1)

        # Plots
        i_clus = np.where(cluster.p_values_ < .01)
        fig = cluster.plot(i_clus=i_clus, show=False)
        report.add_figs_to_section(fig, '{}: {}: Clusters time'.format(ep['name'], contrast['name']),
                                   ep['name'] + contrast['name'])

        fig = cluster.plot_topomap(sensors=False, contours=False, show=False)
        report.add_figs_to_section(fig, '{}: {}: topos'.format(ep['name'], contrast['name']),
                                   ep['name'] + contrast['name'])
        # n = stats.p_values
        # ax = plt.subplots(1,n)
        # for i in range(n):
        #     stats.plot_topo(i, axes=ax[i], title='Cluster #%s' % str(i),
        #                     sensors=False, contours=False)
        # report.add_figs_to_section(fig, '{}: {}: Clusters'.format(ep['name'], contrast['name']),
        #                            ep['name'] + contrast['name'])

        # XXX Save in file

report.save(open_browser=open_browser)
