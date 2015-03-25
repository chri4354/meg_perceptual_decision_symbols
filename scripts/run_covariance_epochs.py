import os.path as op
import numpy as np

import mne
from mne.io.pick import _picks_by_type as picks_by_type
from mne.preprocessing import read_ica

from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from ambiguity.conditions import events_select_condition

from scripts.config import (
    data_path,
    cov_fname_tmp,
    subjects,
    results_dir,
    cov_method,
    epochs_params,
    open_browser,
    missing_mri
)
####################################
####################################
from scripts.config import (
    eog_ch,
    ecg_ch,
    events_fname_filt_tmp,
    ch_types_used,
    epochs_params,
    use_ica,
    raw_fname_filt_tmp,
)
###################################
###################################

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

subjects = [s for s in subjects if s not in missing_mri]

for subject in subjects:
    print(subject)
    # only take prestim covariance
    if False:
        # XXX epoch name should be passsed to config
        epo_fname = op.join(data_path, 'MEG', subject,
            '{}-{}-epo.fif'.format('stim_lock', subject))
        epochs = mne.read_epochs(epo_fname)
    else:
        ########################################################################
        # XXX to be removed once sss head position has been corrected
        ########################################################################
        # ICA
        r = 1 # run 1
        fname = op.join(data_path, 'MEG', subject, raw_fname_filt_tmp.format(r))
        raw = mne.io.Raw(fname)
        set_eog_ecg_channels(raw, eog_ch=eog_ch, ecg_ch=ecg_ch)
        # Select MEG channels
        picks = np.concatenate(
            [p for k, p in picks_by_type(raw.info, meg_combined=True)
             if k in ch_types_used])
        picks = np.concatenate([picks, mne.pick_types(raw.info, meg=False,
                                                      eeg=False, eog=True,
                                                      stim=True)])
        # Get events identified in run_extract_events
        events = mne.read_events(
            op.join(data_path, 'MEG', subject, events_fname_filt_tmp.format(r)))
        # Epoch data for each epoch type
        ep = epochs_params[0]
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
                            events=events_sel, **ep_epochs) #
        # Redefine t0 if necessary
        if 'time_shift' in ep.keys():
            epochs.times += ep['time_shift']
            epochs.tmin += ep['time_shift']
            epochs.tmax += ep['time_shift']

        # ICA correction
        if use_ica:
            icas = list()
            for ch_type in ch_types_used:
                icas.append(read_ica(
                    op.join(data_path, 'MEG', subject,
                            '{}-ica.fif'.format(ch_type))))

            for ica in icas:
                ica.apply(epochs)
        ########################################################################
        ########################################################################


    evoked = epochs.average() # keep for whitening plot
    # pick MEG channels
    # XXX Parameters should be passed to config + should be ch_types
    picks = [epochs.ch_names[i] for i in mne.pick_types(epochs.info, meg=True,
                                                        eeg=False, stim=False,
                                                        eog=False, misc=False,
                                                        exclude='bads')]

    epochs.pick_channels(picks) # XXX need to be simplified in MNE

    # Compute the covariance on baseline
    covs = mne.compute_covariance(
        epochs, tmin=None, tmax=0, method=cov_method,
        return_estimators=True) # XXX add this to config

    for cov in covs:
        # Plot
        fig_cov, fig_svd = mne.viz.plot_cov(cov, epochs.info, colorbar=True,
                                            proj=True, show=True)
        report.add_figs_to_section(fig_cov,
            '{}: covariance ({})'.format(subject, cov['method']), subject)
        report.add_figs_to_section(fig_svd,
            '{}: SVD ({})'.format(subject, cov['method']), subject)

        # plot whitening of evoked response
        fig = evoked.plot_white(cov)
        report.add_figs_to_section(fig,
            '{}: whitened evoked ({})'.format(subject, cov['method']), subject)


        # Save
        cov_fname = op.join(data_path, 'MEG', subject,
                        cov_fname_tmp.format(subject, cov['method']))
        cov.save(cov_fname)

report.save(open_browser=open_browser)
