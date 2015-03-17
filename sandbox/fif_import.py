import mne
datapath = '/media/jrking/harddrive/2013_meg_ambiguity/data/sss/'

# append runs
runs = ['cl120289_main_1_sss.fif',
		'cl120289_main_2_sss.fif',
		'cl120289_main_3_sss.fif',
		'cl120289_main_4_sss.fif',
		'cl120289_main_5_sss.fif',
		'cl120289_main_6_sss.fif',
		'cl120289_main_7_sss.fif',
		'cl120289_main_8_sss.fif',
		'cl120289_main_9_sss.fif',
	    'cl120289_main_10_sss.fif']
#

def preprocess(r):
	# load
	raw = mne.io.Raw(r, preload=True)
	# filter
	raw.filter(1, 30, method='iir')

	# epoch
	events = mne.find_events(raw, stim_channel='STI101', shortest_event=10)
	stim = events[:,2] < 32
	epochs = mne.Epochs(raw, events[stim], None, -0.500, 1.850,
	  					proj=True, baseline=(-0.500, -0.100), preload=False)

	return epochs

epochs = preprocess(datapath+runs[0])

for r in runs[1:]:
	epochs.append(preprocess(datapath + r))


evoked = epochs.average()
evoked.plot()

# get trial conditions
import numpy as np
import scipy.io as sio

filename = '/media/DATA/Pro/Projects/Paris/Categorization/MEG_StringsNumbers/data/behavior/cl_behaviorMEG.mat'
mat = sio.loadmat(filename, squeeze_me=True, struct_as_record=False)
trials = mat['trials']
ttl = [trials[ii].ttl.value for ii in range(len(trials))]
