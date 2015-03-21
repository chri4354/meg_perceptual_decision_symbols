import os
import os.path as op

# PATHS ###############################################################
base_path = op.dirname(op.dirname(__file__))

data_path = op.join(base_path, 'data', 'ambiguity')

pass_errors = False

""" Data paths:
The directory structure should look like this

# MEG directory containing MEG data for each subject
./data/ambiguity/MEG/subject1
./data/ambiguity/MEG/...
./data/ambiguity/MEG/subjectN

# freesurfer directory containing MR data for each subject
./data/ambiguity/subjects/subject1
./data/ambiguity/subjects/...
./data/ambiguity/subjects/subjectN

# other stuff
./data/ambiguity/behavior/
"""

# REPORT ##############################################################
open_browser = True

# SUBJECTS ############################################################
subjects = ['subject01_ar', 'subject02_as', 'subject03_rm',
            'subject04_jm', 'subject05_cl', 'subject06_ha',
            'subject07_sb', 'subject08_pj', 'subject09_kr',
            'subject10_cs', 'subject11_aj', 'subject12_ea',
            'subject13_cg', 'subject14_ap', 'subject15_tb',
            'subject16_mc', 'subject17_az']

# SUBJECT 07: manual fix: head surface is not closed X used original sb-head.fif instead of medium resolution
# SUBJECT 13: manual fix: head surface is not closed X used original sb-head.fif instead of medium resolution
# SUBJECT 05: freesurfer crashed
# SUBJECT 10: freesurfer crashed
# SUBJECT 01: MISSING MRI
# SUBJECT 12: MISSING MRI
# SUBJECT 15: MISSING MRI
# SUBJECT 16: MISSING MRI
# SUBJECT 17: MISSING MRI

missing_mri = ['subject01_ar', 'subject05_cl', 'subject07_sb', 'subject12_ea',
               'subject15_tb', 'subject16_mc', 'subject17_az']

exclude_subjects = [] #missing_mri

subjects = [s for s in subjects if s not in exclude_subjects]

runs = list(range(1, 11, 1))  # 10 runs per subject, starting from 1

# FILRERING ###########################################################
lowpass = 35
highpass = 0.75
filtersize = 16384

# FILENAMES ###########################################################
raw_fname_tmp = 'run_{:02d}_sss.fif'
raw_fname_filt_tmp = 'run_{:02d}_filt-%d-%d_sss_raw.fif' % (highpass, lowpass)
# XXX any reason why -eve. but _raw?
mri_fname_tmp = 'run_{:02d}_sss-trans.fif'
events_fname_filt_tmp = 'run_{:02d}_filt-%d-%d_sss-eve.fif' % (highpass, lowpass)
fwd_fname_tmp = '{:s}-meg-fwd.fif'
inv_fname_tmp = '{:s}-meg-inv.fif'
cov_fname_tmp = '{:s}-meg-cov.fif'
src_fname_tmp = '{:s}-oct-6-src.fif'

# morph_mat_fname_tmp = '{}-morph_mat.mat'



results_dir = op.join(base_path, 'results')
if not op.exists(results_dir):
    os.mkdir(results_dir)

# SELECTION ###########################################################
ch_types_used = ['meg']

# ICA #################################################################
use_ica = True
eog_ch = ['EOG061', 'EOG062']
ecg_ch = 'ECG063'
n_components = 'rank'
n_max_ecg = 4
n_max_eog = 2
ica_reject = dict(mag=5e-12, grad=5000e-13, eeg=300e-6)
ica_decim = 50

# EVENTS ##############################################################
# Exceptional case: subject06 run 9 had a trigger test within the
# recording, need to start collecting events after that/
events_params = dict(subject06_ha=[dict()] * 9 +
                                  [dict(first_sample=140000)])

# EPOCHS ##############################################################
# Generic epochs parameters for stimulus-lock and response-lock
# conditions
event_id = None
cfg = dict(event_id=event_id, decim=4)
# reject=dict(grad=4000e-12, mag=4e-11, eog=180e-5)

# Specific epochs parameters for stim-lock and response-lock conditions
epochs_stim = dict(name='stim_lock', events='stim', tmin=0.110,
                   tmax=1.110, baseline=None, time_shift=-0.430, **cfg)
epochs_resp = dict(name='motor_lock', events='motor', tmin=-0.500,
                   tmax=0.200, baseline=None, **cfg)
epochs_params = [epochs_stim, epochs_resp]

# COV #################################################################
cov_method = ['shrunk', 'empirical']

# INVERSE #############################################################
fsave_grade = 4
# fwd_fname_tmp = 'sub{:02d}-meg-oct-6-fwd.fif' # XXX check file name
make_inverse_params = {'loose': 0.2,
                       'depth': 0.8,
                       'fixed': False,
                       'limit_depth_chs': True}
snr = 3
lambda2 = 1.0 / snr ** 2
apply_inverse_params = {'method': "dSPM", 'pick_ori': None,
                        'pick_normal': None}

# MAIN ANALYSES #######################################################
passive = dict(cond='stim_active', values=[2])
missed = dict(cond='motor_missed', values=[True])
contrasts = (
            dict(name='stim_side',
                 include=dict(cond='stim_side', values=[1, 2]),
                 exclude=[passive]),
            dict(name='stim_category',
                 include=dict(cond='stim_category', values=[0.0, 1.0]),
                 exclude=[passive]),
            dict(name='motor_side',
                 include=dict(cond='motor_side', values=[1, 2]),
                 exclude=[passive, missed]),
            dict(name='motor_category',
                 include=dict(cond='motor_category', values=[0, 1]),
                 exclude=[passive, missed])
            )


decoding_preproc_S = dict(decim=2, crop=dict(tmin=0., tmax=0.700))
decoding_preproc_M = dict(decim=2, crop=dict(tmin=-0.600, tmax=0.100))
decoding_preproc = [decoding_preproc_S, decoding_preproc_M]


# STATS ########################################################################
clu_sigma = 1e3
clu_n_permutations = 1024
clu_threshold = 0.05
