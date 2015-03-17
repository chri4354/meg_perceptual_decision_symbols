import sys
import mkl
import os.path as op
import mne
from meeg_preprocessing.utils import setup_provenance
from ambiguity.conditions import (events_select_condition, extract_events,
                                  get_events)

import matplotlib.pyplot as plt
import warnings

import numpy as np

from scripts.config import (
    data_path,
    subjects,
    results_dir,
    events_fname_filt_tmp,
    open_browser
)

# report, run_id, results_dir, logger = setup_provenance(
#     script=__file__, results_dir=results_dir)
#
# if len(sys.argv) > 1:
#     subjects = [sys.argv[1]]
#     mkl.set_num_threads(1)

# for subject in subjects:
#     # Define data path
#     epochs_fname = op.join(data_path, 'MEG', subject,
#                            'stim-{}-epo.fif'.format(subject))
#     bhv_fname   = op.join(data_path, 'behavior',
#                           '{}_behaviorMEG.mat'.format(subject[-2:]))
#
#     # Read Mat file
#     events = get_stim_events(bhv_fname)
#
#     # Read events from epochs
#     epochs = mne.read_epochs(epochs_fname)
#
#     if not np.all(epochs.events[:,2] == events['trigger_value']):
#         raise('MAT and FIFF events are incompatible')
#     else:
#         mat = events_struct.matrix()
#         M = np.nanmax(mat, axis=0)
#         m = np.nanmin(mat, axis=0)
#         mat -= np.tile(m, (mat.shape[0], 1))
#         mat /= np.tile(M-m, (mat.shape[0], 1))
#         fig = plt.imshow(mat, aspect='auto', interpolation='none')
#         # report.add_figs_to_section(fig, 'all conditions from behavior' , subject)
# #report.save(open_browser=open_browser)  # XXX Check with Denis
#

for subject in subjects[7:]:
    ## stim
    epochs_fname = op.join(data_path, 'MEG', subject,
                           'stim_lock-{}-epo.fif'.format(subject))
    bhv_fname   = op.join(data_path, 'behavior',
                          '{}_behaviorMEG.mat'.format(subject[-2:]))

    # Read Mat file
    events = get_events(bhv_fname, 'stim_lock')
    mat = np.array(events['trigger_value'].astype(list))

    # Read events from epochs
    epochs = mne.read_epochs(epochs_fname)
    fiff = epochs.events[:,2]

    # Checkup procedure
    if len(mat) > len(fiff):
        # XXX Here need procedure to correct issue
        raise('too many events in mat as compared to fiff')
    if len(mat) < len(fiff):
        # XXX Here need procedure to correct issue
        raise('too many events in fiff as compared to mat')

    if np.any(mat != fiff):
        index = np.where((mat - fiff) != 0.)[0][0]
        warnings.warn('{}: Problem with trigger {}.'.format(subject, index))

    fig, (ax1, ax2) = plt.subplots(2, 1, sharey=True)
    ax1.plot(mat)
    ax1.plot(fiff + np.max(mat) + 1.0)
    ax2.plot(mat - fiff)
    ax2.set_title('mat - fiff')
    plt.show()

    # XXX add in report

    ## motor
    epochs_fname = op.join(data_path, 'MEG', subject,
                           'motor_lock-{}-epo.fif'.format(subject))

    # Read Mat file
    events = get_events(bhv_fname, 'motor_lock')
    mat = np.array(events['motor_side'].astype(list))

    # Read events from epochs
    epochs = mne.read_epochs(epochs_fname)
    fiff = 1 + (epochs.events[:,2] < 2 ** 14)

    if len(mat) > len(fiff):
        # XXX Here need procedure to correct issue
        raise('too many events in mat as compared to fiff')
    if len(mat) < len(fiff):
        rm = list()
        index = np.where((mat - fiff[0:len(mat)]) != 0.)[0]
        while (len(index) > 0) and ((len(mat) + len(rm)) <= len(fiff)):
            print(rm)
            rm.append(index[0] + len(rm))
            sel = [i for i in range(0,len(mat)+len(rm)) if i not in rm]
            index = np.where((mat - fiff[sel]) != 0.)[0]
        epochs = epochs[sel]
        warnings.warn('Found {} unwanted epochs. Correcting and resaving {} epochs...'.format(len(rm), subject))
        fiff = 1 + (epochs.events[:,2] < 2 ** 14)
        epochs.save(op.join(data_path, 'MEG', subject, 'stim_lock-{}-epo.fif'.format(subject)))

    fig, (ax1, ax2) = plt.subplots(2, 1, sharey=True)
    ax1.plot(mat)
    ax1.plot(fiff + np.max(mat) + 1.0)
    ax2.plot(mat - fiff)
    ax2.set_title('mat - fiff')
    plt.show()
