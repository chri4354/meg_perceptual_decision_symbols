# Author: Denis A. Engemann <denis.engemann@gmail.com>
# License: BSD (3-clause)

import sys
import mkl
import os.path as op

import mne

from meeg_preprocessing.utils import setup_provenance

from ambiguity.conditions import events_select_condition

from config import (
    data_path,
    subjects,
    runs,
    events_id,
    results_dir,
    events_fname_filt_tmp,
    raw_fname_filt_tmp,
    open_browser
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

if len(sys.argv) > 1:
    subjects = [sys.argv[1]]
    mkl.set_num_threads(1)  # XXX handle MKL

for subject in subjects:
    this_path = op.join(data_path, 'MEG', subject)
    # XXX handle event id
    for run in runs:
        fname = op.join(this_path, raw_fname_filt_tmp.format(run))
        if not op.isfile(fname):
            logger.info('Could not find %s. Skipping' % fname)
            continue
        raw = mne.io.Raw(fname)

        events = mne.find_events(
            raw, stim_channel='STI101', consecutive='increasing',
            min_duration=0.003, verbose=True)

        # XXX  do your events processing and preparation here
        triggers = events[:,2]
        selection = events_select_condition(triggers, 'stim')
        events = events[selection]
        0/0
        mne.write_events(
            op.join(this_path, events_fname_filt_tmp.format(run)), events)

        fig = mne.viz.plot_events(
            events, raw.info['sfreq'], raw.first_samp, show=False,
            event_id=events_id)
        report.add_figs_to_section(fig, 'events run %i' % run, subject)

report.save(open_browser=open_browser)
