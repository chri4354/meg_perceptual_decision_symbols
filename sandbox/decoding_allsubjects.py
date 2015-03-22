import os.path as op
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mne.viz import plot_topomap

import mne
import pickle


###############################################################################

from scripts.config import (
    data_path,
    subjects,
    results_dir,
    epochs_params,
    open_browser,
    contrasts,
)


# Apply contrast on each type of epoch
# for ep in epochs_params:
    # for contrast in contrasts:
ep = epochs_params[0]
contrast = contrasts[1]
for s, subject in enumerate(subjects):
    pkl_fname = op.join(data_path, 'MEG', subject,
                      '{}-{}-decod_{}.pickle'.format(ep['name'], subject,
                                                     contrast['name']))
    with open(pkl_fname) as f:
        gat, contrast = pickle.load(f)
    if s == 0:
        scores = np.array(gat.scores_)[:, :, None]
    else:
        scores = np.concatenate((scores,
                                 np.array(gat.scores_)[:, :, None]),
                                axis=2)



gat.scores_ = np.mean(scores, axis=2)
gat.plot()
gat.plot(vmin=.4, vmax=.6)
gat.plot_diagonal()


diags = np.array([np.diag(score) for score in scores.transpose((2, 0, 1))])
plt.imshow(diags, interpolation='none')
plt.colorbar()
plt.show()

from scipy.stats import wilcoxon
p_values = [wilcoxon(d - .5)[1] for d in diags.transpose()]
