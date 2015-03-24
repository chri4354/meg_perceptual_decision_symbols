import os.path as op
import matplotlib.pyplot as plt

from meeg_preprocessing.utils import setup_provenance

import mne
from mne.minimum_norm import (make_inverse_operator, apply_inverse,
                              write_inverse_operator)

from scripts.config import (
    data_path,
    cov_fname_tmp,
    fwd_fname_tmp,
    inv_fname_tmp,
    src_fname_tmp,
    subjects,
    results_dir,
    epochs_params,
    open_browser,
    missing_mri,
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)


snr = 3.0 # XXX pass to config
lambda2 = 1.0 / snr ** 2

subjects = [s for s in subjects if s not in missing_mri]

for subject in subjects:
    print(subject)
    # setup paths
    epo_fname = op.join(data_path, 'MEG', subject, '{}-{}-epo.fif'.format('stim_lock', subject))
    fwd_fname = op.join(data_path, 'MEG', subject, fwd_fname_tmp.format(subject))
    inv_fname = op.join(data_path, 'MEG', subject, inv_fname_tmp.format(subject))
    cov_fname = op.join(data_path, 'MEG', subject, cov_fname_tmp.format(subject))
    src_fname = op.join(data_path, 'subjects', subject, 'bem',  src_fname_tmp.format(subject))

    # XXX loop across channel types
    # Load data
    epochs = mne.read_epochs(epo_fname)
    evoked = epochs.average() # XXX evoked?
    del epochs
    noise_cov = mne.read_cov(cov_fname)

    forward_meg = mne.read_forward_solution(fwd_fname, surf_ori=True)
    # regularize noise covariance
    noise_cov = mne.cov.regularize(noise_cov, evoked.info,
                                   mag=0.05, grad=0.05, proj=True)

    # Restrict forward solution as necessary for MEG
    forward_meg = mne.pick_types_forward(forward_meg, meg=True, eeg=False)

    # make inverse operators
    info = evoked.info
    inverse_operator_meg = make_inverse_operator(info, forward_meg, noise_cov,
                                                 loose=0.2, depth=0.8)
    # Save
    write_inverse_operator(inv_fname, inverse_operator_meg)

    # Plot report
    # addfig?

# report.save(open_browser=open_browser)

if False:
    # XXX to be passed to another function Compute inverse solution
    stc = apply_inverse(evoked, inverse_operator_meg, lambda2, "dSPM",
                                pick_ori=None)


    ###############################################################################
    # View activation time-series
    fig = plt.figure(figsize=(8, 6))
    plt.plot(1e3 * stc.times, stc.data[::150, :].T)
    plt.ylabel('MEGdSPM value')
    plt.xlabel('Time (ms)')
    plt.show()
