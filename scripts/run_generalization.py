import os.path as op
import numpy as np
import warnings
import mne
from mne.io import Raw
from mne.io.pick import _picks_by_type as picks_by_type
from mne.preprocessing import read_ica
from mne.viz import plot_drop_log
from mne.decoding import GeneralizationAcrossTime
from toolbox.utils import resample_epochs, decim

import pickle

from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from ambiguity.conditions import get_events

from scripts.config import (
    data_path,
    subjects,
    results_dir,
    events_fname_filt_tmp,
    epochs_params,
    open_browser,
    generalizations,
    decoding_preproc,
    decoding_params
)


report, run_id, results_dir, logger = setup_provenance(script=__file__,
                                                       results_dir=results_dir)

mne.set_log_level('INFO')

for subject in subjects:
    # Extract events from mat file
    bhv_fname = op.join(data_path, 'behavior',
                        '{}_behaviorMEG.mat'.format(subject[-2:]))


    # Apply generalization on each type of epoch
    all_epochs = [[]] * len(epochs_params)
    for epoch_params, preproc in zip(epochs_params, decoding_preproc):
        ep_name = epoch_params['name']

        # Get events specific to epoch definition (stim or motor lock)
        events = get_events(bhv_fname, ep_name=ep_name)
        # Get MEG data
        epo_fname = op.join(data_path, 'MEG', subject,
                            '{}-{}-epo.fif'.format(ep_name, subject))
        epochs = mne.read_epochs(epo_fname)

        # preprocess data for memory issue
        if 'resample' in preproc.keys():
            epochs = resample_epochs(epochs, preproc['resample'])
        if 'decim' in preproc.keys():
            epochs = decim(epochs, preproc['decim'])
        if 'crop' in preproc.keys():
            epochs.crop(preproc['crop']['tmin'],
                        preproc['crop']['tmax'])

        # Apply each generalization
        for generalization in generalizations:
            # Find excluded trials
            exclude = np.any([events[x['cond']]==ii
                                for x in generalization['exclude']
                                    for ii in x['values']],
                            axis=0)

            # Select condition
            include = list()
            cond_name = generalization['include']['cond']
            for value in generalization['include']['values']:
                # Find included trials
                include.append(events[cond_name]==value)
            sel = np.any(include,axis=0) * (exclude==False)
            sel = np.where(sel)[0]

            # reduce number or trials if too many
            if len(sel) > 400: # XXX to be removed in final analysis
                import random
                random.shuffle(sel)
                sel = sel[0:400]

            if len(sel) == 0:
                warnings.warn('%s: no epoch in %s for %s.' % (subject, ep_name,
                                                        generalization['name']))
                continue

            y = np.array(events[cond_name].tolist())

            # Load GAT
            pkl_fname = op.join(data_path, 'MEG', subject,
                                '{}-{}-decod_{}.pickle'.format(ep_name,
                                subject, generalization['contrast']))
            with open(pkl_fname) as f:
                gat, contrast = pickle.load(f)

            gat.predict_mode = 'mean-prediction'
            gat.score(epochs[sel], y=y[sel])

            # Plot
            fig = gat.plot_diagonal(show=False)
            report.add_figs_to_section(fig, ('%s (%s): %s -> %s' %
                (subject, ep_name,
                 generalization['contrast'],
                 generalization['name'])), subject)

            fig = gat.plot(show=False)
            report.add_figs_to_section(fig, ('%s (%s): %s -> %s' %
                (subject, ep_name,
                 generalization['contrast'],
                 generalization['name'])), subject)

            # Save generalization
            gat.estimators_ = None # Avoid memory issues
            pkl_fname = op.join(data_path, 'MEG', subject,
                                '{}-{}-generalize_{}.pickle'.format(ep_name,
                                subject, generalization['name']))
            with open(pkl_fname, 'w') as f:
                pickle.dump([gat, generalization], f)

report.save(open_browser=open_browser)
