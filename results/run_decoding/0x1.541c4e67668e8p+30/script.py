import os.path as op
import numpy as np
import mne
from mne.io import Raw
from mne.io.pick import _picks_by_type as picks_by_type
from mne.preprocessing import read_ica
from mne.viz import plot_drop_log
from mne.decoding import GeneralizationAcrossTime

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
    contrasts,
)


report, run_id, results_dir, logger = setup_provenance(script=__file__,
                                                       results_dir=results_dir)

mne.set_log_level('INFO')

for subject in subjects:

    # Extract events from mat file
    bhv_fname = op.join(data_path, 'behavior',
                        '{}_behaviorMEG.mat'.format(subject[-2:]))


    # Apply contrast on each type of epoch
    all_epochs = [[]] * len(epochs_params)
    for epoch_params in epochs_params:
        ep_name = epoch_params['name']

        # Get events specific to epoch definition (stim or motor lock)
        events = get_events(bhv_fname, ep_name=ep_name)
        # Get MEG data
        epo_fname = op.join(data_path, 'MEG', subject,
                            '{}_{}-epo.fif'.format(ep_name, subject))
        epochs = mne.read_epochs(epo_fname)

        # Decim epochs for speed issues
        # epochs.resample(125, n_jobs=-1)  # XXX check with denis
        # epochs.crop(0., .500)

        # Apply each contrast
        for contrast in contrasts:
            # Find excluded trials
            exclude = np.any([events[x['cond']]==ii
                                for x in contrast['exclude']
                                    for ii in x['values']],
                            axis=0)

            # Select condition
            include = list()
            cond_name = contrast['include']['cond']
            for value in contrast['include']['values']:
                # Find included trials
                include.append(events[cond_name]==value)
            sel = np.any(include,axis=0) * (exclude==False)
            sel = np.where(sel)[0]

            # reduce number or trials if too many
            if len(sel) > 400:
                import random
                random.shuffle(sel)
                sel = sel[0:400]

            y = np.array(events[cond_name].tolist())

            # Apply contrast
            # from sklearn.preprocessing import StandardScaler
            # from sklearn.pipeline import Pipeline
            # from sklearn.svm import SVC
            # scaler = StandardScaler()
            # svc = SVC(C=1, kernel='linear', probability=True)
            # clf = Pipeline([('scaler', scaler), ('svc', svc)])
            # gat = GeneralizationAcrossTime(n_jobs=-1, clf=clf,
            #                                predict_type='predict_proba')
            gat = GeneralizationAcrossTime(n_jobs=-1)
            gat.fit(epochs[sel], y=y[sel])
            gat.score(epochs[sel], y=y[sel])

            # Plot
            fig = gat.plot_diagonal()
            report.add_figs_to_section(fig, ('%s: %s (decoding)'
                                             % (ep_name, cond_name)),
                                       subject)

            fig = gat.plot()
            report.add_figs_to_section(fig, ('%s: %s (GAT)'
                                             % (ep_name, cond_name)),
                                       subject)
            # Save contrast
            pkl_fname = op.join(data_path, 'MEG', subject,
                                '{}-{}_decod-{}.pickle'.format(ep_name, subject,
                                                               cond_name))
            with open(pkl_fname, 'w') as f:
                pickle.dump([gat, contrast], f)

report.save(open_browser=open_browser)
