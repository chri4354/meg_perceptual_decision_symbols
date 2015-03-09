# Author: Denis A. Engemann <denis.engemann@gmail.com>
# License: BSD (3-clause)

import os.path as op

from mne.io.pick import pick_types as picks_by_type
from mne.io import Raw
from meeg_preprocessing import compute_ica
from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from config import (
    data_path,
    subjects,
    runs,
    results_dir,
    raw_fname_filt_tmp,
    n_components,
    n_max_ecg,
    n_max_eog,
    ica_reject,
    ica_decim,
    open_browser
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

for subject in subjects:  # XXX if needed compute run-wise
    this_path = op.join(data_path, 'MEG', subject)
    fname = op.join(this_path, raw_fname_filt_tmp.format(runs[0]))
    raw = Raw(fname, preload=True)
    for run in runs[1:]:
        fname = op.join(this_path, raw_fname_filt_tmp.format(run))
        if not op.isfile(fname):
            logger.info('Could not find %s. Skipping' % fname)
            continue
        raw.append(Raw(fname, preload=True))

    set_eog_ecg_channels(raw)  # XXX check

    for ch_type, picks in picks_by_type(raw.info, meg_combined=True):
        ica, _ = compute_ica(
            raw, picks=picks, subject=subject, n_components=n_components,
            n_max_ecg=n_max_ecg, n_max_eog=n_max_eog, reject=ica_reject,
            decim=ica_decim, report=report)
        ica.save(
            op.join(this_path, '{}-ica.fif'.format(ch_type)))

report.save(open_browser=open_browser)
