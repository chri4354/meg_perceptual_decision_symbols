
import mne
import numpy as np
import warnings
import scipy.io as sio
from toolbox.jr_toolbox import struct

def events_select_condition(trigger, condition):
    """Function to handle events and event ids

    Parameters
    ----------
    trigger : np.array (dims = [n,1])
        The trigger values
    condition : str
        The set of events corresponding to a specific analysis.

    Returns
    -------
    selection : np.array (dims = [m, 1])
        The selected trigger.
    """
    if condition == 'stim_motor':
        selection = np.where(trigger > 0)[0]
    elif condition == 'stim':
        selection = np.where((trigger > 0) & (trigger < 64))[0]
    elif condition == 'motor':  # remove response not linked to stim
        selection = np.where((trigger > 64) & (trigger != 128))[0]
    return selection

def get_events_stim(bhv_fname, ep_name='both'):
    """"Get events from matlab file"""
    import pandas as pd

    trials = sio.loadmat(bhv_fname, squeeze_me=True,
                         struct_as_record=True)["trials"]

    # Redefine key to be more explicit
    keys = [('type', 'stim_active', int),
            ('side', 'stim_side', int),
            ('amb', 'stim_category', float),
            ('amb_word', 'stim_category', float),
            ('key', 'motor_side', int),
            ('correct', 'motor_correct', float),
            ('RT_MEG', 'motor_RT', float),
            ('choice', 'motor_category', int),
            ('choice_bar', 'motor_contrast', float)] # XXX still need to formally check choice and choice_bar

    # Create indexable dictionary
    events = list()
    for ii, trial in enumerate(trials):
        event = dict()
        # add already present fields
        for key in keys:
            event[key[1]] = trial[key[0]]

        # Add manual fields
        event['trigger_value'] = int(trial['ttl']['value'])
        event['trial_number'] = ii

        # ---- stimulus categorical ambiguity
        # NB: There seems to be an error in the matlab postproc code regarding
        # trials.amb_word. We thus need to redefine the conditions properly.
        if trial['target_code'] in [1, 2]: # [['540', 'SHO'], ['560', 'SEO']]
            events['stim_category'] = trial['amb'] / 8
        elif trial['target_code'] in [3, 5]: # [[540, 590],  [560, 580]]
            events['stim_category'] = 0.0
        elif trial['target_code'] in [4, 6]: # [[SHO, SAO],  [SEO, SCO]]
            events['stim_category'] = 1.0
        else:
            raise('problem target_code!')

        # ---- stimulus contrast
        if trial['target_code'] in [1, 3, 4, 5]:
            events['stim_contrast'] = events['stim_category']
        elif: trial['target_code'] in [2, 6]:
            events['stim_contrast'] = 1 - events['stim_category']
        else:
            raise('problem target_code!')

        # Concatenate stim event
        if (ep_name == 'stim_lock' or ep_name == 'both'):
            event['event_type'] = 'stim'
            events.append(event)
        # Concatenate motor event if expect one
        if (ep_name == 'motor_lock' or ep_name == 'both'):
            if event['motor']:
                eventm = event
                eventm['event_type'] = 'motor'
                events.append(eventm)
    events_df = pd.DataFrame(events)
    return events_df


def extract_events(fname, min_duration=0.003):
    """Function to 1) recompute STI101 from other channels
                   2) clean trigger channel
                   3) Add stimulus information to response channel

    Parameters
    ----------
    fname : str
        The filename of the event dataset.
    min_duration : float
        The minimum duration (in s) of an event

    Returns
    -------
    events : np.array (dims = [n_events, 3])
        Events array to pass to MNE.
    """
    import sys
    import os.path as op

    # Load data
    raw = mne.io.Raw(fname, preload=True)
    # Min duration in sample
    min_sample = min_duration * raw.info['sfreq']

    # 1. Combine STI channels
    S_ch = ['STI001', 'STI002', 'STI003', 'STI004', 'STI005', 'STI006']
    M_ch = ['STI013', 'STI015']
    raw.pick_channels(S_ch + M_ch)

    # Binarize trigger values from 5 mV to 0 and 1
    raw._data = np.round(raw._data / 5)
    cmb_S, sample_S = _combine_events(raw._data[0:len(S_ch)], min_sample)
    cmb_M, sample_M = _combine_events(raw._data[len(S_ch):], min_sample)

    # Correct order of magnitude of M response to avoid S/M conflict
    cmb_M *= (2 ** len(S_ch))

    # Get trigger values for stim and unassociated motor
    trigger_S, trigger_M = cmb_S[sample_S], cmb_M[sample_M]

    # Find first M response following trigger
    max_delay = raw.info['sfreq'] * 3.000
    sample_MS, trigger_MS = [], []
    for s, S in enumerate(sample_S):
        # Find first M response
        M = np.where(np.array(sample_M) > S)[0]
        # Check its link to S
        if (any(M) and (sample_M[M[0]] - S) < max_delay):
            # Associate S value to M to link the two
            trigger_M[M[0]] += trigger_S[s]

    # Combine S and M events
    events_S = [sample_S, np.zeros(len(sample_S)), trigger_S]
    events_M = [sample_M, np.zeros(len(sample_M)), trigger_M]
    events = np.hstack((events_S, events_M)).transpose()

    # Sort events by sample
    events = events[np.argsort(events[:, 0]), :]

    # Add starting sample
    events[:,0] += raw.first_samp

    return events

def _combine_events(data, min_sample):  # GENERIC TRIGGER FUNCTION
    """ Function to combine multiple trigger channel in a single binary code """
    n_chan, n_sample = data.shape
    cmb = np.zeros([n_chan, n_sample])
    for bit in range(0, n_chan):
        cmb[bit, :] = 2 ** bit * data[bit, :]
    cmb = np.sum(cmb, axis=0)

    # Find trigger onsets and offset
    diff = cmb[1:] - cmb[0:-1]
    onset = np.where(diff > 0)[0] + 1
    offset = np.where(diff < 0)[0]

    # minimum changing time
    onset_t = np.where((onset[1:] - onset[:-1]) > min_sample)[0]
    onset = onset[np.append(onset_t, len(onset_t))]
    offset_t = np.where((offset[1:] - offset[:-1]) > min_sample)[0] + 1
    offset = offset[np.append(0, offset_t)]

    # Correct inequality of triggers' onsets and offsets
    if offset[0] < onset[0]:
        offset = offset[1:]
    if len(onset) > len(offset):
        #onset = onset[:-1]
        offset = np.hstack((offset, onset[-1] + min_sample))
        warnings.warn("Added extra offset!")

    # Remove too short samples
    duration = offset - onset
    sample = onset[duration > min_sample].tolist()

    return cmb, sample
