import mne
import numpy as np
from toolbox.jr_toolbox import my_resample
from scipy.signal import resample
import numpy as np
import matplotlib.pyplot as plt
from ambiguity.conditions import events_select_condition, get_events

bhv_fname = 'data/ambiguity/behavior/cl_behaviorMEG.mat'
epo_fname = 'data/ambiguity/MEG/subject05_cl/motor_lock-subject05_cl-epo.fif'

mat_events = np.array(get_events(bhv_fname, ep_name='motor_lock')['motor_side'].astype(list))

epochs = mne.read_epochs(epo_fname)
sel = events_select_condition(epochs.events[:,2], 'motor')
epochs = epochs[sel]
epo_events = 1. + (epochs.events[:, 2] < 16000)

plt.plot(mat_events[0:100],'r')
plt.plot(epo_events[0:100],'b')

plt.plot(mat_events - epo_events[range(0,1480) + range(1481, 1601)],'g')
plt.show()
