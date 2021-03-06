# Author: Denis A. Engemann <denis.engemann@gmail.com>
# License: BSD (3-clause)

import mkl
import sys
import os.path as op
import numpy as np
import mne
from mne.io import Raw
from mne.io.pick import _picks_by_type as picks_by_type
from mne.preprocessing import read_ica
from mne.viz import plot_drop_log

from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from ambiguity.conditions import events_select_condition

from config import (
    data_path,
    subjects,
    runs,
    results_dir,
    raw_fname_filt_tmp,
    eog_ch,
    ecg_ch,
    events_fname_filt_tmp,
    ch_types_used,
    epochs_params,
    use_ica,
    open_browser
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)


mne.set_log_level('INFO')

if len(sys.argv) > 1:
    subjects = [sys.argv[1]]
    mkl.set_num_threads(1)

for subject in subjects:
    this_path = op.join(data_path, 'MEG', subject)
    epochs_list_stim = list()
    epochs_list_resp = list()

    icas = list()
    if use_ica is True:
        for ch_type in ch_types_used:
            icas.append(read_ica(
                op.join(this_path, '{}-ica.fif'.format(ch_type))))
    for run in runs:
        fname = op.join(this_path, raw_fname_filt_tmp.format(run))
        if not op.isfile(fname):
            logger.info('Could not find %s. Skipping' % fname)
            continue

        raw = Raw(fname)

        # Set ECG EOG channels XXX again?
        set_eog_ecg_channels(raw, eog_ch=eog_ch, ecg_ch=ecg_ch)

        # Interpolate bad channels
        if 'eeg' in ch_types_used and len(raw.info['bads']) > 0:
            raw.interpolate_bad_channels()

        # Select MEG channels
        picks = np.concatenate(
            [p for k, p in picks_by_type(raw.info, meg_combined=True)
             if k in ch_types_used])
        picks = np.concatenate([picks, mne.pick_types(raw.info, meg=False,
                                                      eeg=False, eog=True,
                                                      stim=True)])

        # Get events identified in run_extract_events
        events = mne.read_events(
            op.join(this_path, events_fname_filt_tmp.format(run)))

        # Epoch data for each epoch type
        for ep, epochs_list in zip(epochs_params,
                                   [epochs_list_stim, epochs_list_resp]):
            # Select events
            sel = events_select_condition(events[:,2], ep['events'])
            events_sel = events[sel,:]

            # Only keep parameters applicable to mne.Epochs()
            ep_epochs = {key:v for key, v in ep.items() if key in ['event_id',
                                                               'tmin', 'tmax',
                                                               'baseline',
                                                               'reject',
                                                               'decim']}
            # Epoch raw data
            epochs = mne.Epochs(raw=raw, picks=picks, preload=True,
                                events=events_sel, **ep_epochs)

            # Redefine t0 if necessary
            if 'time_shift' in ep.keys():
                epochs.times += ep['time_shift']
                epochs.tmin += ep['time_shift']
                epochs.tmax += ep['time_shift']

            # ICA correction
            if use_ica is True:
                for ica in icas:
                    ica.apply(epochs)

            # Append runs
            epochs_list.append(epochs)

    # Save and report
    for name, epochs_list in zip(['stim', 'motor'],
                                 [epochs_list_stim, epochs_list_resp]):
        # Concatenate runs
        epochs = mne.epochs.concatenate_epochs(epochs_list)

        # Plot
        #-- % dropped
        report.add_figs_to_section(
            plot_drop_log(epochs.drop_log), 'total dropped {}'.format(
                name), subject)
        #-- % trigger channel
        trigger_ch = mne.pick_channels(epochs.ch_names, 'STI101')
        epochs._data[:, trigger_ch,:] = np.log(epochs._data[:, trigger_ch,:])
        fig = mne.viz.plot_image_epochs(epochs, trigger_ch,
                                        scalings=dict(stim=132),
                                        units=dict(stim=''))
        report.add_figs_to_section(fig, 'STI101 %s' % name, subject)

        #-- % evoked
        evoked = epochs.average()
        fig = evoked.plot()
        report.add_figs_to_section(fig, 'Mean ERF %s: butterfly' % name,
                                   subject)
        times = np.arange(epochs.tmin, epochs.tmax,
                          (epochs.tmax - epochs.tmin) / 20)
        fig = evoked.plot_topomap(times, ch_type='mag')
        report.add_figs_to_section(fig, 'Mean ERF %s: topo' % name, subject)

        # Save
        epochs.save(op.join(this_path, '{}-{}-epo.fif'.format(name, subject)))

report.save(open_browser=open_browser)
