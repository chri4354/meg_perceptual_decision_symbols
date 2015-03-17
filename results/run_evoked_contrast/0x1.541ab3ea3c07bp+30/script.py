import os.path as op
import numpy as np
import mne
from mne.io import Raw
from mne.io.pick import _picks_by_type as picks_by_type
from mne.preprocessing import read_ica
from mne.viz import plot_drop_log
from mne.decoding import GeneralizationAcrossTime

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

# for subject in subjects:
subject = subjects[0] # XXX enable loop across subjects
# Extract events from mat file
bhv_fname = op.join(data_path, 'behavior',
                    '{}_behaviorMEG.mat'.format(subject[-2:]))
events = get_events(bhv_fname)

# Apply contrast on each type of epoch
all_epochs = [[]] * len(epochs_params)
for epoch_param in epochs_params:
    name = epoch_param['name']
    epo_fname = op.join(data_path, 'MEG', subject,
                        '{}-{}-epo.fif'.format(name, subject))
    epochs = mne.read_epochs(epo_fname)
    # Decim epochs for speed issues
    # epochs.resample(125, n_jobs=-1)  # XXX check with denis
    # epochs.crop(0., .500)

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
            evoked = epochs[include * exclude].average()
            evoked.comment = contrast['include']['cond']+str(value)
            evoked.tmin, evoked.tmin = epochs.tmin, epochs.tmax # XXX mne bug
            evokeds.append(evoked)

        # Apply contrast
        contrast = evokeds[0] - evokeds[1]

        # Plot
        fig = contrast.plot()
        report.add_figs_to_section(fig, '%s' % name, subject)
        plot_times = np.linspace(contrast.tmin, contrast.tmax, 10)
        fig = contrast.plot_topomap(plot_times, ch_type='mag')
        report.add_figs_to_section(fig, '%s' % name, subject)
        print('ok')

report.save(open_browser=open_browser)
