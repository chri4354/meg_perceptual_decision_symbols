import os.path as op
import numpy as np
import mne
from mne.io import Raw
from mne.io.pick import _picks_by_type as picks_by_type
from mne.preprocessing import read_ica
from mne.viz import plot_drop_log
from mne.decoding import GeneralizationAcrossTime

from meeg_preprocessing.utils import setup_provenance, set_eog_ecg_channels

from ambiguity.conditions import get_events

data_path = 'data/ambiguity'
events_fname_filt_tmp = 'run_{:02d}_filt-0-30_sss-eve.fif'
epoch_params = dict(name='stim_lock', events='stim', tmin=0.310, tmax=1.210,
                   baseline=None, time_shift=-0.410, event_id=None,
                   reject=dict(grad=4000e-12, mag=4e-11, eog=180e-5), decim = 16)


passive = dict(cond='stim_active', values=[2])
missed = dict(cond='motor', values=[0])
contrast = dict(include=dict(cond='stim_category', values=[0.0, 1.0]),
                exclude=[passive])

subject = 'subject05_cl'

bhv_fname = op.join(data_path, 'behavior',
                    '{}_behaviorMEG.mat'.format(subject[-2:]))


# Apply contrast on each type of epoch
ep_name = epoch_params['name']

# Get events specific to epoch definition (stim or motor lock)
events = get_events(bhv_fname, ep_name=ep_name)
# Get MEG data
epo_fname = op.join(data_path, 'MEG', subject,
                    '{}-{}-epo.fif'.format(ep_name, subject))
epochs = mne.read_epochs(epo_fname)

# Decim epochs for speed issues
# epochs.resample(125, n_jobs=-1)  # XXX check with denis
# epochs.crop(0., .500)


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

if len(sel) > 400:
    import random
    random.shuffle(sel)
    sel = sel[0:400]

y = np.array(events[cond_name].tolist())

# Apply contrast
gat = GeneralizationAcrossTime(n_jobs=-1)
gat.fit(epochs[sel], y=y[sel])
scores=gat.score(epochs[sel], y=y[sel])
gat.plot()
gat.plot_diagonal()
