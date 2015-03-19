def resample_epochs(epochs, sfreq):
    """faster resampling"""
    # from librosa import resample
    # librosa.resample(channel, o_sfreq, sfreq, res_type=res_type)
    from scipy.signal import resample
    import numpy as np

    # resample
    epochs._data = resample(epochs._data,
                            epochs._data.shape[2] / epochs.info['sfreq'] * sfreq,
                            axis=2)
    # update metadata
    epochs.info['sfreq'] = sfreq
    epochs.times = (np.arange(epochs._data.shape[2],
                              dtype=np.float) / sfreq + epochs.times[0])
    return epochs

def decim(inst, decim):
    """faster resampling"""
    from mne.io.base import _BaseRaw
    from mne.epochs import _BaseEpochs
    if isinstance(inst, _BaseRaw):
         inst._data =  inst._data[:,::decim]
         inst.info['sfreq'] /= decim
         inst._first_samps /= decim
         inst.first_samp /= decim
         inst._last_samps /= decim
         inst.last_samp /= decim
         inst._raw_lengths /= decim
         inst._times =  inst._times[::decim]
    elif isinstance(inst, _BaseEpochs):
        inst._data = inst._data[:,:,::decim]
        inst.info['sfreq'] /= decim
        inst.times = inst.times[::decim]
    return inst
