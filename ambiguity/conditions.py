
import mne
import numpy as np
import warnings
import scipy.io as sio

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
        selection = np.where((trigger > 0) & (trigger < 4096))[0]
    elif condition == 'motor':  # remove response not linked to stim
        #selection = np.where((trigger > 64) & (trigger != 128))[0]
        selection = np.where(trigger >= 4096)[0]
    return selection

def get_events(bhv_fname, ep_name='both'):
    """"Get events from matlab file

    Parameters
    ----------
    bhv_fname : str
        mat file path with behavioral results
    ep_name : str (default: 'both')
        string indicating if output corresponds to 'stim' events, 'motor' events
        or 'both'

    Returns
    -------
    events_df : pd.DataFrame
    """
    import pandas as pd

    trials = sio.loadmat(bhv_fname, squeeze_me=True,
                         struct_as_record=True)["trials"]

    # Redefine key to be more explicit
    keys = [('side', 'stim_side', int),
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
        event['stim_active'] = trial['type'] == 1
        event['trigger_value'] = int(trial['ttl']['value'])
        event['motor_missed'] = not(event['motor_RT'] > 0.)
        event['trial_number'] = ii

        # ---- stimulus categorical ambiguity
        # NB: There seems to be an error in the matlab postproc code regarding
        # trials.amb_word. We thus need to redefine the conditions properly.
        if trial['target_code'] in [1, 2]: # [['540', 'SHO'], ['560', 'SEO']]
            event['stim_category'] = (trial['amb'] - 1.0) / 7.0
        elif trial['target_code'] in [3, 5]: # [[540, 590],  [560, 580]]
            event['stim_category'] = 0.0
        elif trial['target_code'] in [4, 6]: # [[SHO, SAO],  [SEO, SCO]]
            event['stim_category'] = 1.0
        else:
            raise('problem target_code!')

        # ---- type of passive stimulus
        if not(event['stim_active']):
            # [[540, 590],  [560, 580], [SHO, SAO],  [SEO, SCO]]
            if trial['amb'] == 1:
                event['stim_new'] = 0
            elif trial['amb'] == 8:
                event['stim_new'] = 1
            else:
                raise('problem target code')
        else:
            event['stim_new'] = 0


        # ---- stimulus contrast
        if trial['target_code'] in [1, 3, 4, 5]:
            event['stim_contrast'] = event['stim_category']
        elif trial['target_code'] in [2, 6]:
            event['stim_contrast'] = 1.0 - event['stim_category']
        else:
            raise('problem target_code!')

        # Concatenate stim event
        if (ep_name == 'stim_lock' or ep_name == 'both'):
            event['event_type'] = 'stim'
            events.append(event)

        # Add motor event subject responded so as to get a single events
        # structure for both stim and resp lock
        if (ep_name == 'motor_lock' or ep_name == 'both'):
            if event['stim_active']:
                event_ = event.copy()
                event_['event_type'] = 'motor'
                events.append(event_)

    # store and panda DataFrame for easier manipulation
    events_df = pd.DataFrame(events)
    return events_df


def extract_events(fname, min_duration=0.003, first_sample=0,
                   offset_to_zero_M=True, offset_to_zero_S=False):
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

    # Dissociate STI101 into distinct channels
    raw.pick_channels(['STI101'])
    n_bits = 16
    raw._data = np.round(raw._data)
    data = np.zeros((n_bits, raw.n_times))
    for bit in range(0, n_bits)[::-1]:
        data[bit, :] = (raw._data >= 2 ** bit).astype(float)
        raw._data -= data[bit, :] * (2 ** bit)

    # Min duration in sample
    min_sample = min_duration * raw.info['sfreq']

    # Binarize trigger values to 0 and 1
    S_ch = range(0, 11)
    M_ch = range(11, n_bits)
    # Get all motor events, independently of task relevance
    cmb_M_, sample_M_ = _combine_events(data[len(S_ch):,:], min_sample,
                                      first_sample=first_sample,
                                      overlapping=False,
                                      offset_to_zero=offset_to_zero_M)
    # Only consider stim triggers after first button response (to avoid trigger
    # test trhat shouldn't have been recorded)
    cmb_S, sample_S = _combine_events(data[0:len(S_ch),:], min_sample,
                                      first_sample=sample_M_[0],
                                      overlapping=True,
                                      offset_to_zero=offset_to_zero_S)

    # Correct order of magnitude of M response to avoid S/M conflict
    cmb_M_ *= (2 ** len(S_ch))

    # Get trigger values for stim and unassociated motor
    trigger_S, trigger_M_ = cmb_S[sample_S], cmb_M_[sample_M_]

    # Select M responses relevant to task: first M response following trigger
    #max_delay = raw.info['sfreq'] * (2.000 + .430)
    sample_M, trigger_M = list(), list()
    for s, S in enumerate(sample_S):
        # Find first M response
        M = np.where(np.array(sample_M_) > S)[0]
        # Check its link to S
        # if (any(M) and (sample_M_[M[0]] - S) <= max_delay):
        if any(M):
            if trigger_S[s] <= 4.0: # Don't create trigger if stim is in passive condition
                # Add motor response to motor
                sample_M.append(sample_M_[M[0]])
                # Associate S value to M to link the two
                trigger_M.append(trigger_M_[M[0]] + trigger_S[s])

    # Combine S and M events
    events_S = [sample_S, np.zeros(len(sample_S)), trigger_S]
    events_M = [sample_M, np.zeros(len(sample_M)), trigger_M]
    events = np.hstack((events_S, events_M)).transpose()

    # Sort events chronologically
    events = events[np.argsort(events[:, 0]), :]

    # Add starting sample
    events[:,0] += raw.first_samp

    return events

def _combine_events(data, min_sample, first_sample=0, overlapping=True,
                    offset_to_zero=True):
    """ Function to combine multiple trigger channel in a single binary code """
    n_chan, n_sample = data.shape
    cmb = np.zeros([n_chan, n_sample])
    for bit in range(0, n_chan):
        cmb[bit, :] = 2 ** bit * data[bit, :]
    cmb = np.sum(cmb, axis=0)

    if not overlapping:
        over_t = np.where(np.sum(data, axis=0) > 1.0)[0]
        cmb[over_t] = 0.0

    # Find trigger onsets and offsets
    diff = cmb[1:] - cmb[0:-1]
    diff[:first_sample] = 0  # don't consider triggers before this
    onset = np.where(diff > 0)[0] + 1
    offset = np.where(diff < 0)[0]

    # minimum changing time
    onset_t = np.where((onset[1:] - onset[:-1]) >= min_sample)[0]
    onset = onset[np.append(onset_t, len(onset_t))]
    offset_t = np.where((offset[1:] - offset[:-1]) >= min_sample)[0] + 1
    offset = offset[np.append(0, offset_t)]

    # first offsets should be after first onset
    if offset[0] < onset[0]:
        offset = offset[1:]
    # offsets must go back to 0
    if offset_to_zero:
        offset = offset[np.where(cmb[offset+1] == 0.)[0]]
    # XXX should do the same for onset?:
    # onset = onset[np.where(cmb[onset-1] == 0.)[0]]
    if len(onset) > len(offset):
        #onset = onset[:-1]
        offset = np.hstack((offset, onset[-1] + min_sample))
        warnings.warn("Added extra offset!")

    # Remove too short samples
    duration = offset - onset
    sample = onset[duration > min_sample].tolist()

    return cmb, sample
