import os.path as op
import numpy as np
import matplotlib.pyplot as plt
import mayavi

from meeg_preprocessing.utils import setup_provenance

import mne
from mne.viz import plot_trans

from scripts.config import (
    data_path,
    raw_fname_tmp,
    trans_fname_tmp,
    subjects,
    results_dir,
    open_browser,
    missing_mri
)

report, run_id, results_dir, logger = setup_provenance(
    script=__file__, results_dir=results_dir)

subjects = [s for s in subjects if s not in missing_mri]

for subject in subjects:
    raw = mne.io.Raw(op.join(data_path, 'MEG', subject,
                                raw_fname_tmp.format(1)), preload=False)


    scene = plot_trans(raw.info, op.join(data_path, 'MEG', subject,
                                    trans_fname_tmp.format(1)),
                                    subject=subject,
                                    subjects_dir=op.join(data_path,'subjects'),
                                    source='head')

    views = np.array(([90, 90], [0, 90], [0, -90], [0, 0]))
    fig, ax = plt.subplots(1, len(views))
    for i, v in enumerate(views):
        mayavi.mlab.view(v[0], v[1], figure=scene)
        img = mayavi.mlab.screenshot()
        ax[i].imshow(img)
        ax[i].axis('off')

    report.add_figs_to_section(fig, '{}'.format(subject), subject)

report.save(open_browser=open_browser)
