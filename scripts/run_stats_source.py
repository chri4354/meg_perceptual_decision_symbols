import os.path as op
import pickle
import numpy as np
import matplotlib.pyplot as plt
import mayavi
from scipy import stats as stats
from scipy.ndimage import zoom

import mne
from mne import (spatial_tris_connectivity, compute_morph_matrix,
                 grade_to_tris)
from mne.minimum_norm import apply_inverse, read_inverse_operator
from mne.stats import (spatio_temporal_cluster_1samp_test,
                       summarize_clusters_stc)

from meeg_preprocessing.utils import setup_provenance

from scripts.config import (
    data_path,
    subjects,
    missing_mri,
    results_dir,
    events_fname_filt_tmp,
    epochs_params,
    open_browser,
    contrasts,
    inv_fname_tmp, # XXX add contrast name in congi
)


# mne.set_log_level('INFO')

# report, run_id, results_dir, logger = setup_provenance(script=__file__,
#                                                        results_dir=results_dir)

subjects = [s for s in subjects if s not in missing_mri] # XXX

# define connectivity
connectivity = spatial_tris_connectivity(grade_to_tris(5))

# Read all inverse operators
inverse_operator = dict()
sample_vertices = dict()
for subject in subjects:
    inv_fname = op.join(data_path, 'MEG', subject,
                        inv_fname_tmp.format(subject))
    inv = read_inverse_operator(inv_fname)
    inverse_operator[subject] = inv
    sample_vertices[subject] = [s['vertno'] for s in inv['src']]

# Prepare morphing matrix : # XXX should be done externally?
morph_mat = dict()
for subject in subjects:
    smooth = 20
    fsave_vertices = [np.arange(10242), np.arange(10242)]
    morph_mat[subject] = compute_morph_matrix(subject, 'fsaverage',
                                              sample_vertices[subject],
                                              fsave_vertices, smooth,
                                              op.join(data_path, 'subjects'))

for epoch_params in epochs_params:
    for contrast in contrasts:
        # Concatenate data across subjects
        X = list()
        for subject in subjects:
            # Read evoked data for each condition
            ave_fname = op.join(data_path, 'MEG', subject,
                                '{}-{}-contrasts-ave.fif'.format(
                                epoch_params['name'], subject))
            evokeds = list()
            for v in contrast['include']['values']:
                evoked = mne.read_evokeds(ave_fname,
                                          condition=contrast['name']+str(v))

                # Apply inverse operator
                snr = 3.0 # XXX pass to config
                lambda2 = 1.0 / snr ** 2
                evoked = apply_inverse(evoked, inverse_operator[subject],
                                       lambda2, 'dSPM')
                evokeds.append(evoked)

            # Contrast # XXX that morph is linear
            # XXX abs(evoked.data)?
            diff = evokeds[0] - evokeds[-1]

            # Morph
            n_vertices_fsave = morph_mat[subject].shape[0]
            x = np.reshape(diff.data, (diff.data.shape[0], len(diff.times)))
            x = morph_mat[subject].dot(x)  # morph_mat is a sparse matrix
            x = x.reshape(n_vertices_fsave, len(diff.times))
            X.append(x)

        # with open('all_inv_morphed', 'w') as f:
        #     pickle.dump([X, diff, subjects, epoch_params, morph_mat, fsave_vertices,
        #                 contrast, inverse_operator, sample_vertices], f)

        # Stats
        threshold = -stats.distributions.t.ppf(.05 / 2., len(subjects) - 1)
        T_obs, clusters, cluster_p_values, H0 = clu = \
            spatio_temporal_cluster_1samp_test(np.transpose(X, (0, 2, 1)),
                                               connectivity=connectivity,
                                               n_jobs=-1,
                                               threshold=threshold)
        good_cluster_inds = np.where(cluster_p_values < 0.05)[0]

        diff._data = np.zeros(np.shape(X)[1:])
        for c in good_cluster_inds:
            for t, v in zip(clusters[c][0], clusters[c][1]):
                diff._data[v, t] = -np.log10(cluster_p_values[c])

        # significant times
        times_inds = [round(np.mean([clusters[c][0]])) for c in good_cluster_inds]
        plot_times = [int(diff.times[t] * 1000) for t in times_inds]
        min_p_value = -np.log10(np.min(cluster_p_values))

        # Plot
        brain = diff.plot('fsaverage', subjects_dir=op.join(data_path, 'subjects'),
                           surface='inflated', config_opts=dict(height=300., width=600))

        stc_all_cluster_vis = summarize_clusters_stc(clu, tstep=diff.tstep,
                                                     vertices=fsave_vertices,
                                                     subject='fsaverage')

        # brain = stc_all_cluster_vis.plot('fsaverage', 'inflated', 'split',
        #                                  subjects_dir=op.join(data_path, 'subjects'),
        #                                  config_opts=dict(height=300., width=600),
        #                                  time_label='Duration significant (ms)')
        # color scale
        brain.scale_data_colormap(0, min_p_value / 2, min_p_value, True)
        # XXX Start from here


        # if 'imgs' in locals(): del imgs
        # for t in plot_times:
            # print(t)
        img = []
        # for hemi in range(1):
             brain.set_time(t)
            # x = brain.texts_dict['time_label']['text']
            # x.set(text=x.get('text')['text'][5:-6])
            # x.set(width=0.3 * len(x.get('text')['text']))
            img.append(np.hstack(brain.save_imageset(None,
                views=['lateral', 'medial', 'ventral'], colorbar=None, col=hemi)))
        img = np.vstack(img)
        # img = np.array([zoom(c, 600. / img.shape[0])
        #         for c in img.transpose((2, 0, 1))]).transpose((1, 2, 0))
            # if not 'imgs' in locals():
            #     imgs = img
            # else:
            #     imgs = np.concatenate((imgs, img), axis=1)

        fig, ax = plt.subplots(1, figsize=(15,20)) #
        ax.imshow(img)
        ax.axis('off')
        report.add_figs_to_section(fig, contrast['name'], subject)

# report.save(open_browser=True)
