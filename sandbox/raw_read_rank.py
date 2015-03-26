from scripts.config import subjects
import mne
from mne.preprocessing import read_ica
from scripts.config import subjects, ch_types_used

data_path = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/MEG/'

ranks = []
for subject in subjects:
    rank = []
    for r in range(1, 11):
        raw = mne.io.Raw(data_path + subject + '/run_{:02d}_filt-0-35_sss_raw.fif'.format(r), preload=False)
        rank.append(mne.io.proc_history._get_sss_rank(raw.info['proc_history'][0]['max_info']))
    ranks.append([rank])


# read ica components
n = []
for subject in subjects:
    for ch_type in ch_types_used:
        ica = mne.preprocessing.read_ica(data_path +  subject + '/{}-ica.fif'.format(ch_type))
        n.append(ica.n_components)


# Try reading one run with and without ICA
