import sys
import mkl
import os.path as op
import mne
from meeg_preprocessing.utils import setup_provenance
from ambiguity.conditions import get_events

import matplotlib.pyplot as plt
import warnings

import numpy as np

from scripts.config import (
    data_path,
    subjects,
    results_dir,
    open_browser
)


report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

# if len(sys.argv) > 1:
#     subjects = [sys.argv[1]]
#     mkl.set_num_threads(1)

for subject in subjects:
    # STIM =====================================================================
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
        raise(error)
        # warnings.warn('{}: too many events in mat as compared to fiff'.format(subject))
        # mat = mat[0:len(fiff)]
    if len(mat) < len(fiff):
        raise(error)
        # warnings.warn('{}: too many events in fiff as compared to mat'.format(subject))
        # fiff = fiff[0:len(mat)]

    if np.any(mat != fiff):
        index = np.where((mat - fiff) != 0.)[0][0]
        warnings.warn('{}: Problem with trigger {}.'.format(subject, index))

    # Report
    fig, (ax1, ax2) = plt.subplots(2, 1, sharey=True)
    ax1.plot(mat)
    ax1.plot(fiff + np.max(mat) + 1.0)
    ax2.set_title('triggers from mat & fiff')
    ax2.plot(mat - fiff)
    ax2.set_title('mat - fiff')
    report.add_figs_to_section(fig, 'Stim triggers', subject)
    # plt.show()


    # MOTOR ====================================================================
    epochs_fname = op.join(data_path, 'MEG', subject,
                           'motor_lock-{}-epo.fif'.format(subject))

    # Read Mat file
    events = get_events(bhv_fname, 'motor_lock')
    mat = np.array(events['motor_side'].astype(list))

    # Read events from epochs
    epochs = mne.read_epochs(epochs_fname)
    m = np.where(epochs.events[:,2] < 2 ** 14)[0]
    fiff = 1 + (epochs.events[:,2] < 2 ** 14)

    if len(mat) > len(fiff):
        # mat = mat[0:len(fiff)]
        # rm = list()
        # index = np.where((fiff - mat[0:len(fiff)]) != 0.)[0]
        # wg = 0
        # while (len(index) > 0) and ((len(fiff) + len(rm)) < len(mat)):
        #     # test if just wrong trigger
        #     sel = [i for i in range(0,len(fiff)+len(rm)) if i not in rm]
        #     wrong = sum(abs(fiff - mat[sel]))
        #     # test if additional trigger
        #     sel = [i for i in range(0,len(fiff)+len(rm)+1) if i not in (rm+[index[wg] + len(rm)])]
        #     addup =  sum(abs(fiff - mat[sel]))
        #     if addup >= wrong:
        #         rm.append(index[wg] + len(rm))
        #     else:
        #         wg += 1
        #     index = np.where((fiff - mat[sel]) != 0)[0]
        # mat = mat[sel]
        # print('{}: found {} unwanted mat M events. Correcting and NOT resaving mat...'.format(subject, len(rm)))
        # XXX NEED TO DO SOMETHING ABOUT IT HERE!
        raise(error)

    if len(mat) < len(fiff):
        # # fiff = fiff[0:len(mat)]
        # rm = list()
        # index = np.where((mat - fiff[0:len(mat)]) != 0.)[0]
        # while (len(index) > 0) and ((len(mat) + len(rm)) < len(fiff)):
        #     rm.append(index[0] + len(rm))
        #     sel = [i for i in range(0,len(mat)+len(rm)) if i not in rm]
        #     index = np.where((mat - fiff[sel]) != 0.)[0]
        #     print('remove {}'.format(rm[-1]))
        # epochs = epochs[sel]
        # print('{}: found {} unwanted M epochs. Correcting and resaving epochs...'.format(subject, len(rm)))
        # fiff = 1 + (epochs.events[:,2] < 2 ** 14)
        # epochs.save(epochs_fname)
        raise(error)


    fig, (ax1, ax2) = plt.subplots(2, 1, sharey=True)
    ax1.plot(mat)
    ax1.plot(fiff + np.max(mat) + 1.0)
    ax2.set_title('triggers from mat & fiff')
    ax2.plot(mat - fiff)
    ax2.set_title('mat - fiff')
    report.add_figs_to_section(fig, 'Motor triggers', subject)
    # plt.show()

# report.save(open_browser=open_browser)
#
# fig, ax = plt.subplots(10, 1, sharey=True)
# for ii in range(0,10):
#     sel = ii*200 + np.arange(0,200)
#     ax[ii].plot(fiff[sel]+0.1)
#     ax[ii].plot(mat[sel])
# plt.show()
