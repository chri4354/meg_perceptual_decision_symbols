import os.path as op
import numpy as np
import mne
from mne.io import Raw
from mne.io.pick import _picks_by_type as picks_by_type
from mne.preprocessing import read_ica
from mne.viz import plot_drop_log

from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from ambiguity.conditions import get_events

from config import (
    data_path,
    subjects,
    results_dir,
    events_fname_filt_tmp,
    epochs_params,
    open_browser,
    contrasts,
)


report, run_id, results_dir, logger = setup_provenance(script=__file__,
                                                       results_dir=results_dir)

mne.set_log_level('INFO')

for subject in subjects:
    # Extract events from mat file
    bhv_fname = op.join(data_path, 'behavior',
                        '{}_behaviorMEG.mat'.format(subject[-2:]))


    # Apply contrast on each type of epoch
    all_epochs = [[]] * len(epochs_params)
    for epoch_params in epochs_params:
        ep_name = epoch_params['name']

        # Get events specific to epoch definition (stim or motor lock)
        events = get_events(bhv_fname, ep_name=ep_name)
        # Get MEG data
        epo_fname = op.join(data_path, 'MEG', subject,
                            '{}-{}-epo.fif'.format(ep_name, subject))
        epochs = mne.read_epochs(epo_fname)

        # Apply each contrast
        for contrast in contrasts:
            evokeds = list()

            # Find excluded trials
            exclude = np.any([events[x['cond']]==ii
                                for x in contrast['exclude']
                                    for ii in x['values']],
                            axis=0)

            # Select condition
            for value in contrast['include']['values']:
                # Find included trials
                include = events[contrast['include']['cond']]==value
                # Evoked data
                evoked = epochs[include * (exclude==False)].average()
                evoked.comment = contrast['include']['cond']+str(value)
                evokeds.append(evoked)

            # Apply contrast
            contrast = evokeds[0] - evokeds[1]

            # Plot
            fig = contrast.plot()
            report.add_figs_to_section(fig, ('%s: %s (butterfly)'
                                             % (ep_name, contrast.comment)),
                                       subject)
            plot_times = np.linspace(contrast.times.min(),
                                     contrast.times.max(),
                                     10)
            fig = contrast.plot_topomap(plot_times, ch_type='mag')
            report.add_figs_to_section(fig, ('%s: %s (topo)'
                                             % (ep_name, contrast.comment)),
                                       subject)
            # Save contrast
            ave_fname = op.join(data_path, 'MEG', subject,
                                '{}-{}-{}-ave.fif'.format(ep_name, subject,
                                                          contrast.comment))
            contrast.save(ave_fname)

report.save(open_browser=open_browser)
