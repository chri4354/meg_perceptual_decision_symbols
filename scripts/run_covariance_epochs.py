import os.path as op

from meeg_preprocessing.utils import setup_provenance

import mne

from scripts.config import (
    data_path,
    raw_fname_tmp,
    mri_fname_tmp,
    cov_fname_tmp,
    subjects,
    results_dir,
    cov_method,
    epochs_params,
    open_browser,
    missing_mri
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

subjects = [s for s in subjects if s not in missing_mri]

for subject in subjects:
    print(subject)
    # only take prestim covariance
    epo_fname = op.join(data_path, 'MEG', subject, '{}-{}-epo.fif'.format('stim_lock', subject)) # XXX should be passsed to config
    epochs = mne.read_epochs(epo_fname)
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

    for cov in covs:
        # Save
        cov_fname = op.join(data_path, 'MEG', subject,
                    cov_fname_tmp.format(subject, cov['method']))
        cov.save(cov_fname)

        # Plot
        fig_cov, fig_svd = mne.viz.plot_cov(cov, epochs.info, colorbar=True,
                                            proj=True, show=False)
        report.add_figs_to_section(fig_cov, '{}: covariance ({})'.format(subject, cov['method']), subject)
        report.add_figs_to_section(fig_svd, '{}: SVD ({})'.format(subject, cov['method']), subject)

        # plot whitening of evoked response
        fig = evoked.plot_white(cov)
        report.add_figs_to_section(fig, '{}: whitened evoked ({})'.format(subject, cov['method']), subject)

report.save(open_browser=open_browser)
