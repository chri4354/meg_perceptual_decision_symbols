import os.path as op
import numpy as np
import matplotlib.pyplot as plt
import mayavi
from scipy.ndimage import zoom

import mne
from mne.minimum_norm import apply_inverse, read_inverse_operator
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


mne.set_log_level('INFO')

report, run_id, results_dir, logger = setup_provenance(script=__file__,
                                                       results_dir=results_dir)

subjects = [s for s in subjects if s not in missing_mri]

for subject in subjects:
    this_path = op.join(data_path, 'MEG', subject) + '/'
    for epoch_params in epochs_params:

        # Read inverse operator
        inv_fname = this_path + inv_fname_tmp.format(subject)
        inverse_operator = read_inverse_operator(inv_fname)

        # Apply each contrast
        ave_fname = this_path + '{}-{}-contrasts-ave.fif'.format(
                    epoch_params['name'], subject)

        for contrast in contrasts:
            evokeds = list()
            for v in contrast['include']['values']:
                evoked = mne.read_evokeds(ave_fname,
                                          condition=contrast['name']+str(v))
                # Apply inverse operator
                snr = 3.0 # XXX pass to config
                lambda2 = 1.0 / snr ** 2
                evoked = apply_inverse(evoked, inverse_operator, lambda2,
                                       'dSPM')
                evokeds.append(evoked)

            # Contrast
            diff = evokeds[0] - evokeds[-1]

            # Plot
            cmap = plt.get_cmap('RdBu_r')
            cmap._init()
            cmap = cmap._lut[:cmap.N,:] * 255
            cmap[:, -1] = np.linspace(-1.0, 1.0, cmap.shape[0]) ** 2 * 255

            brain = diff.plot(subject,
                              subjects_dir=op.join(data_path, 'subjects'),
                              surface='inflated', hemi='split',
                              colormap=cmap, config_opts=dict(height=300.,
                              width=600, offscreen=True))

            mM = np.max([abs(np.min(diff.data)), abs(np.max(diff.data))])
            brain.scale_data_colormap(-mM, 0, mM, False)

            # XXX
            if epoch_params['name'] == 'stim_lock':
                plot_times = np.linspace(0, 600, 12)
            else:
                plot_times = np.linspace(-500, 100, 12)

            if 'imgs' in locals(): del imgs
            for t in plot_times:
                print(t)
                img = []
                for hemi in range(2):
                    brain.set_time(t)
                    x = brain.texts_dict['time_label']['text']
                    x.set(text=x.get('text')['text'][5:-6])
                    x.set(width=0.1 * len(x.get('text')['text']))
                    img.append(np.vstack(brain.save_imageset(None,
                        views=['lateral', 'medial'], colorbar=None, col=hemi)))
                img = np.vstack(img)
                img = np.array([zoom(c, 600. / img.shape[0])
                        for c in img.transpose((2, 0, 1))]).transpose((1, 2, 0))
                if not 'imgs' in locals():
                    imgs = img
                else:
                    imgs = np.concatenate((imgs, img), axis=1)

            fig, ax = plt.subplots(1, figsize=(15,20)) #
            ax.imshow(imgs)
            ax.axis('off')
            report.add_figs_to_section(fig, contrast['name'], subject)

report.save(open_browser=True)
