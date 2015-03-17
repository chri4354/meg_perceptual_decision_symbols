import sys
import mkl
import os.path as op
import mne
from meeg_preprocessing.utils import setup_provenance
from ambiguity.conditions import (events_select_condition, extract_events,
                                  get_events)

import matplotlib.pyplot as plt

import numpy as np

from config import (
    data_path,
    subjects,
    results_dir,
    events_fname_filt_tmp,
    open_browser
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

if len(sys.argv) > 1:
    subjects = [sys.argv[1]]
    mkl.set_num_threads(1)

for subject in subjects:
    # Define data path
    epochs_fname = op.join(data_path, 'MEG', subject,
                           'stim-{}-epo.fif'.format(subject))
    bhv_fname   = op.join(data_path, 'behavior',
                          '{}_behaviorMEG.mat'.format(subject[-2:]))

    # Read Mat file
    events = get_stim_events(bhv_fname)

    # Read events from epochs
    epochs = mne.read_epochs(epochs_fname)

    if not np.all(epochs.events[:,2] == events_struct.get('trigger_value')):
        raise('MAT and FIFF events are incompatible')
    else:
        mat = events_struct.matrix()
        M = np.nanmax(mat, axis=0)
        m = np.nanmin(mat, axis=0)
        mat -= np.tile(m, (mat.shape[0], 1))
        mat /= np.tile(M-m, (mat.shape[0], 1))
        fig = plt.imshow(mat, aspect='auto', interpolation='none')
        # report.add_figs_to_section(fig, 'all conditions from behavior' , subject)
#report.save(open_browser=open_browser)  # XXX Check with Denis
