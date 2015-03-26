#!/usr/bin/env bash

STUDY_PATH=$1
export SUBJECT=$2

cd ${STUDY_PATH} && export SUBJECTS_DIR=${PWD}/subjects
cd -
cd ${STUDY_PATH}/MEG/${SUBJECT} && export MEG_DIR=`pwd`
cd -

# # Source space
mne_setup_source_space --ico -6 --overwrite
# #
# # # Prepare for forward computation
mne_setup_forward_model --homog --surf --ico 4
# mne_setup_forward_model --surf --ico 4

#
# # cd $MEG_DIR
#
# # Compute ECG SSP projection vectors. The produced file will also include the SSP projection vectors currently in the raw file
# mne compute_proj_ecg -i run_01_raw.fif -c "EEG063" --l-freq 1 --h-freq 100 \
#     --rej-grad 3000 --rej-mag 4000 --rej-eeg 120 --average --proj ${SUBJECT}_ecg_proj.fif
#
# # Do the same for EOG. Also include the projection vectors from the previous step, so that the file contains all projection vectors
# mne compute_proj_eog -i run_01_raw.fif -c "EEG062" --l-freq 1 --h-freq 35 \
#     --rej-grad 3000 --rej-mag 4000 --rej-eeg 120 --no-proj --average \
#     --proj ${SUBJECT}_eog_proj.fif

##############################################################################
# Compute forward solution a.k.a. lead field

cd $MEG_DIR

# # for MEG only
# mne_do_forward_solution --src ${SUBJECTS_DIR}/${SUBJECT}/bem/${SUBJECT}-morph-oct-6-src.fif \
#         --meas run_01_raw.fif --bem ${SUBJECT}-5120 --megonly --overwrite \
#         --fwd ${SUBJECT}-meg-morph-oct-6-fwd.fif

# # for MEG only
mne_do_forward_solution --mindist 5 --spacing oct-6 \
        --meas run_01_raw.fif --bem ${SUBJECT}-5120 --megonly --overwrite \
        --fwd ${SUBJECT}-meg-oct-6-fwd.fif

# # for both EEG and MEG
# mne_do_forward_solution --mindist 5 --spacing oct-6 \
#         --meas run_01_raw.fif --bem ${SUBJECT}-5120-5120-5120 \
#         --fwd ${SUBJECT}-meg-eeg-oct-6-fwd.fif
#
# exit 0
