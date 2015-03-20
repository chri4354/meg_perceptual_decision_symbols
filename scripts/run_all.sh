# Freesurfer
sh scripts/run_freesurfer_recon-all.sh
ipython scripts/run_check_freesurfer.py
sh scripts/run_check_recon-all.sh

# MNE
ipython scripts/run_mne_coregistration.sh

# MNE-python
ipython scripts/run_filtering.py
ipython scripts/run_ica.py
ipython scripts/run_extract_events.py
ipython scripts/run_extract_epochs.py
ipython scripts/run_check_epochs.py

ipython scripts/run_setup_forward.py

ipython scripts/run_evoked_contrast.py
ipython scripts/run_decoding.py
