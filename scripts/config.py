import os
import os.path as op

# PATHS ########################################################################
base_path = op.dirname(op.dirname(__file__))

data_path = op.join(base_path, 'data', 'ambiguity')

pass_errors = False

""" Data path notes

link your data against data_path

the directory structure should look like this

# MEG directory containing MEG data for each subject
./data/ambiguity/MEG/subject1
./data/ambiguity/MEG/...
./data/ambiguity/MEG/subjectN

# freesurfer directory containing MR data for each subject
./data/ambiguity/subjects/subject1
./data/ambiguity/subjects/...
./data/ambiguity/subjects/subjectN

# other stuff
./data/ambiguity/behavioral/
"""

results_dir = op.join(base_path, 'results')

if not op.exists(results_dir):
    os.mkdir(results_dir)


# REPORT
open_browser = True

# SUBJECTS #####################################################################
subjects = ['subject01_ar', 'subject02_as', 'subject03_rm', 'subject04_jm',
      'subject05_cl', 'subject06_ha', 'subject07_sb', 'subject08_pj',
      'subject09_kr', 'subject10_cs', 'subject11_aj', 'subject12_ea',
      'subject13_cg', 'subject14_ap', 'subject15_tb', 'subject16_mc',
      'subject17_az']

# subjects = ['subject05_cl']

exclude_subjects = []  # XXX add subject names here if you wan't to exclude

runs = list(range(1, 11, 1))  # 10 runs per subject

# FILRERING ####################################################################
lowpass = 30
highpass = 0.75
filtersize = 16384  # XXX check with denis
decim = 1

# FILENAMES ####################################################################
# XXX update file name templates
raw_fname_tmp = 'run_{:02d}_sss.fif'
raw_fname_filt_tmp = 'run_{:02d}_filt-%d-%d_sss_raw.fif' % (
    highpass, lowpass)
events_fname_filt_tmp = 'run_{:02d}_filt-%d-%d_sss-eve.fif' % (
    highpass, lowpass) # XXX any reason why -eve. but _raw?
forward_fname_tmp = '{}-meg-oct-6-fwd.fif'
morph_mat_fname_tmp = '{}-morph_mat.mat'

# SELECTION ####################################################################
ch_types_used = ['meg']

# ICA ##########################################################################
use_ica = True
eog_ch = ['EOG061', 'EOG062']
ecg_ch = 'ECG063'
n_components = 'rank'
n_max_ecg = 4
n_max_eog = 2
ica_reject = dict(mag=5e-12, grad=5000e-13, eeg=300e-6)
ica_decim = 15  # XXX adjust depending on data

# EPOCHS #######################################################################
# Generic epochs parameters for stimulus-lock and response-lock conditions
event_id = None
cfg = dict(event_id=event_id,
           reject=dict(grad=4000e-12, mag=4e-11, eog=180e-5),
           decim = 16)

# Specific epochs parameters for stimulus-lock and response-lock conditions
epochs_stim = dict(name='stim_lock', events='stim', tmin=0.310, tmax=1.210,
                   baseline=None, time_shift=-0.410, **cfg)
epochs_resp = dict(name='motor_lock', events='motor', tmin=-0.500, tmax=0.200,
                   baseline=None, **cfg)
epochs_params = [epochs_stim, epochs_resp]

# COV ##########################################################################
cov_method = ['shrunk', 'empirical']

# INVERSE ######################################################################

fsave_grade = 4

fwd_fname_tmp = 'sub{:02d}-meg-oct-6-fwd.fif'  #

make_inverse_params = {'loose': 0.2,
                       'depth': 0.8,
                       'fixed': False,
                       'limit_depth_chs': True}
snr = 3
lambda2 = 1.0 / snr ** 2
apply_inverse_params = {'method': "dSPM", 'pick_ori': None, 'pick_normal': None}

# MAIN #########################################################################
passive = dict(cond='active', values=[2])
contrasts = (
            dict(include=dict(cond='stim_side', values=[1, 2]),
                 exclude=[passive]),
            dict(include=dict(cond='stim_category', values=[1, 8]),
                exclude=[passive]),
            dict(include=dict(cond='motor_side', values=[1, 2]),
                 exclude=[passive]),
            dict(include=dict(cond='motor_category', values=[1, 2]),
                 exclude=[passive])
            )



# STATS ########################################################################

clu_sigma = 1e3
clu_n_permutations = 1024
clu_threshold = 0.05
