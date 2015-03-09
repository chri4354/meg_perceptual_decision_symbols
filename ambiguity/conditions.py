

def epochs_select_condition(epochs, selection):
    """Function to handle events and event ids

    Parameters
    ----------
    epochs : instance of mne.Epochs
        The raw data.
    selection : str
        The set of events corresponding to a specific analysis.

    Returns
    -------
    epochs : mne.Epochs
        The epochs
    """
    if selection == 'all':
        pass
    elif selection == 'motor':
        pass
    # ... make selection
    # ... insert meaningful event id names
    #  mne.epochs.combine_event_ids(epochs, old_event_ids, new_event_id, copy=True)
    #  mne.epochs.concatenate_epochs(epochs_list)
    # numpy indexing
    # epochs.events_id = dict(...)
    pass
