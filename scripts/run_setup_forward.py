import mne
import os.path as op
from meeg_preprocessing.utils import setup_provenance
import matplotlib.pyplot as plt

from scripts.config import (
    data_path,
    raw_fname_tmp,
    mri_fname_tmp,
    fwd_fname_tmp,
    subjects,
    results_dir,
    open_browser,
    missing_mri
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

subjects = [s for s in subjects if s not in missing_mri]

for subject in subjects:
    print(subject)
    # setup paths
    raw_fname = op.join(data_path, 'MEG', subject, raw_fname_tmp.format(1))
    mri = op.join(data_path, 'MEG', subject, mri_fname_tmp.format(1))
    bem = op.join(data_path, 'subjects', subject, 'bem',  subject + '-5120-bem-sol.fif')
    src = op.join(data_path, 'subjects', subject, 'bem',  subject + '-oct-6-src.fif')

    # setup source space
    mne.setup_source_space(subject, subjects_dir=op.join(data_path, 'subjects'),
                           overwrite=True, n_jobs=6)

    # forward solution
    fwd = mne.make_forward_solution(raw_fname, mri=mri, src=src, bem=bem,
                                    fname=None, meg=True, eeg=False, mindist=5.0,
                                    n_jobs=2, overwrite=True) # XXX if too many jobs, conflict between MKL and joblib

    # convert to surface orientation for better visualization
    fwd = mne.convert_forward_solution(fwd, surf_ori=True)
    leadfield = fwd['sol']['data']

    print("Leadfield size : %d x %d" % leadfield.shape)

    grad_map = mne.sensitivity_map(fwd, ch_type='grad', mode='fixed')
    mag_map = mne.sensitivity_map(fwd, ch_type='mag', mode='fixed')

    # SAVE
    fwd_fname = op.join(data_path, 'MEG', subject, fwd_fname_tmp.format(subject))
    mne.write_forward_solution(fwd_fname, fwd, overwrite=True)

    # PLOT
    picks = mne.pick_types(fwd['info'], meg=True, eeg=False)
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    fig.suptitle('Lead field matrix (500 dipoles only)', fontsize=14)
    im = ax.imshow(leadfield[picks, :500], origin='lower', aspect='auto',
                   cmap='RdBu_r')
    ax.set_xlabel('sources')
    ax.set_ylabel('sensors')
    plt.colorbar(im, ax=ax, cmap='RdBu_r')
    report.add_figs_to_section(fig, '{}: Lead field matrix'.format(subject), subject)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.hist([grad_map.data.ravel(), mag_map.data.ravel()],
             bins=20, label=['Gradiometers', 'Magnetometers'],
             color=['c', 'b'])
    ax.legend()
    ax.set_title('Normal orientation sensitivity')
    ax.set_xlabel('sensitivity')
    ax.set_ylabel('count')
    report.add_figs_to_section(fig, '{}: Normal orientation sensitivity'.format(subject), subject)

report.save(open_browser=open_browser)
