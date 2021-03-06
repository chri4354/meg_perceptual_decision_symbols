# Author: Denis A. Engemann <denis.engemann@gmail.com>
# License: BSD (3-clause)

import os.path as op

from mne.io.pick import _picks_by_type as picks_by_type
from mne.io import Raw

from meeg_preprocessing import compute_ica
from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from config import (
    data_path,
    subjects,
    runs,
    results_dir,
    raw_fname_filt_tmp,
    eog_ch,
    ecg_ch,
    n_components,
    n_max_ecg,
    n_max_eog,
    ica_reject,
    ica_decim,
    open_browser,
    ch_types_used
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

for subject in subjects:
    print(subject)
    this_path = op.join(data_path, 'MEG', subject)
    for r in range(0, len(runs)):
        fname = op.join(this_path, raw_fname_filt_tmp.format(runs[r]))
        if not op.isfile(fname):
            logger.info('Could not find %s. Skipping' % fname)
            continue
        raw_ = Raw(fname, preload=True)
        # decimate
        decim_ = 10
        raw_._data = raw_._data[:,::decim_]
        raw_.info['sfreq'] /= decim_
        raw_._first_samps /= decim_
        raw_.first_samp /= decim_
        raw_._last_samps /= decim_
        raw_.last_samp /= decim_
        raw_._raw_lengths /= decim_
        raw_._times = raw_._times[::decim_]

        # Append
        if r == 0:
            raw = raw_
        else:
            raw.append(raw_)

    set_eog_ecg_channels(raw, eog_ch=eog_ch, ecg_ch=ecg_ch)

    for ch_type, picks in picks_by_type(raw.info, meg_combined=True):
        if ch_type not in ch_types_used:
            continue
        ica, _ = compute_ica(
            raw, picks=picks, subject=subject, n_components=n_components,
            n_max_ecg=n_max_ecg, n_max_eog=n_max_eog, reject=ica_reject,
            decim=ica_decim, report=report)
        ica.save(
            op.join(this_path, '{}-ica.fif'.format(ch_type)))
    del raw

# XXX NOT CONVERGING FOR SUBJECT01 ASK DENIS + MEMORY ERROR
report.save(open_browser=open_browser)
