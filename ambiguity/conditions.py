import numpy as np

def epochs_select_condition(epochs, condition):
    """Function to handle events and event ids

    Parameters
    ----------
    epochs : instance of mne.Epochs
        The raw data.
    condition : str
        The set of events corresponding to a specific analysis.

    Returns
    -------
    epochs : mne.Epochs
        The epochs
    """


    triggers = epochs.events[:,2]
    selection = events_select_condition(triggers, condition)

    epochs = epochs[selection]

    # ... make selection
    # ... insert meaningful event id names
    #  mne.epochs.combine_event_ids(epochs, old_event_ids, new_event_id, copy=True)
    #  mne.epochs.concatenate_epochs(epochs_list)
    # numpy indexing
    # epochs.events_id = dict(...)
    # pass


def events_select_condition(triggers, condition):
    """Function to handle events and event ids

    Parameters
    ----------
    triggers : np.array (dims = [n,1])
        The trigger values
    condition : str
        The set of events corresponding to a specific analysis.

    Returns
    -------
    selection : np.array (dims = [m, 1])
        The selected triggers.
    """
    if condition == 'all':
        selection = np.where(triggers > 0)
    elif condition == 'stim':
        selection = np.where((triggers > 0 ) & (triggers < 32))
    elif condition == 'stim_left':
        pass
    elif condition == 'stim_right':
        pass
    elif condition == 'motor':
        selection = np.where(triggers > 32)
    elif condition == 'motor_left':
        pass
    elif condition == 'motor_right':
        pass
    return selection
