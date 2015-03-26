import mkl
import sys
import os.path as op
import numpy as np
import mne
from mne.io import Raw
from mne.io.pick import _picks_by_type as picks_by_type # XXX users should not need this
from mne.preprocessing import read_ica
from mne.viz import plot_drop_log

from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from ambiguity.conditions import events_select_condition

from scripts.config import (
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
    open_browser,
    raw_fname_tmp,
    mri_fname_tmp,
    cov_fname_tmp,
    cov_method,
    epochs_params,
    missing_mri
)


subject = subjects[0]
run = runs[0:2]

this_path = op.join(data_path, 'MEG', subject)
all_epochs = [] # XXX should be generic to take len(epochs_params)

# ICA?
icas = list()
for ch_type in ch_types_used:
    icas.append(read_ica(
        op.join(this_path, '{}-ica.fif'.format(ch_type))))

# EPOCHS #######################################################################
for r in runs:
    # for r in runs:
    fname = op.join(this_path, raw_fname_filt_tmp.format(r))
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
        op.join(this_path, events_fname_filt_tmp.format(r)))
    # Epoch data for each epoch type
    ep = epochs_params[0]
    epochs_list = all_epochs
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
                        events=events_sel, reject=dict(grad=4000e-12, mag=4e-11, eog=180e-5), **ep_epochs) #
    # Redefine t0 if necessary
    if 'time_shift' in ep.keys():
        epochs.times += ep['time_shift']
        epochs.tmin += ep['time_shift']
        epochs.tmax += ep['time_shift']
    # ICA correction
    if True:
        for ica in icas:
            ica.apply(epochs)

    # Append runs
    epochs_list.append(epochs)

epochs = mne.epochs.concatenate_epochs(epochs_list)

epochs = epochs[:192]

# ICA ##########################################################################
evoked = epochs.average() # keep for whitening plot
# pick MEG channels
picks = [epochs.ch_names[i] for i in mne.pick_types(epochs.info, meg=True,
                                                    eeg=False, stim=False,
                                                    eog=False,
                                                    exclude='bads')]  # XXX should be passed to config + should be ch_types

epochs.pick_channels(picks) # XXX need to be simplified in MNE


# Compute the covariance on baseline
covs = mne.compute_covariance(
    epochs, tmin=None, tmax=0, method=cov_method,
    return_estimators=True) # XXX add this to config

cov = covs[0]
# Save
cov_fname = op.join(data_path, 'MEG', subject,
            cov_fname_tmp.format(subject, cov['method']))

# Plot
fig_cov, fig_svd = mne.viz.plot_cov(cov, epochs.info, colorbar=True, proj=True)

# plot whitening of evoked response
fig = evoked.plot_white(cov)
