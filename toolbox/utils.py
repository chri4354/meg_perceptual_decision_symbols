import numpy as np

def resample_epochs(epochs, sfreq):
    """faster resampling"""
    # from librosa import resample
    # librosa.resample(channel, o_sfreq, sfreq, res_type=res_type)
    from scipy.signal import resample

    # resample
    epochs._data = resample(epochs._data,
                            epochs._data.shape[2] / epochs.info['sfreq'] * sfreq,
                            axis=2)
    # update metadata
    epochs.info['sfreq'] = sfreq
    epochs.times = (np.arange(epochs._data.shape[2],
                              dtype=np.float) / sfreq + epochs.times[0])
    return epochs

def decim(inst, decim):
    """faster resampling"""
    from mne.io.base import _BaseRaw
    from mne.epochs import _BaseEpochs
    if isinstance(inst, _BaseRaw):
         inst._data =  inst._data[:,::decim]
         inst.info['sfreq'] /= decim
         inst._first_samps /= decim
         inst.first_samp /= decim
         inst._last_samps /= decim
         inst.last_samp /= decim
         inst._raw_lengths /= decim
         inst._times =  inst._times[::decim]
    elif isinstance(inst, _BaseEpochs):
        inst._data = inst._data[:,:,::decim]
        inst.info['sfreq'] /= decim
        inst.times = inst.times[::decim]
    return inst


class cluster_stat(dict):
    """"""
    def __init__(self, insts, pos=None, alpha=0.05, p_threshold=0.001,
                 t_threshold=None, connectivity='neuromag306mag', n_jobs=-1):
        """"""
        from mne.evoked import Evoked
        from mne.epochs import _BaseEpochs

        # intialize vars
        init = lambda: [list() for i in range(len(insts))]
        signals, conds, times, comments, chans = \
            init(), init(), init(), init(), init()

        # for each condition, extract data and meta data
        for inst, signal, time, comment, chan in \
            zip(insts, signals, times, comments, chans):
            if isinstance(inst, list):
                if not np.all([isinstance(x, Evoked) for x in inst]):
                    raise('inst must be a list of Evokeds or an Epochs object')
                # concatenate signals
                signal.append([x.data for x in inst])
                # extract meta data
                summarize = lambda x: x[0] if np.all([i == x[0] for i in x]) else None
                time.append(summarize([x.times for x in inst]))
                comment.append(summarize([x.comment for x in inst]))
                chan.append(summarize([x.ch_names for x in inst]))
            elif isinstance(inst, _BaseEpochs):
                signal.append(x._data)
                time.append(x.time)
                comments.append(x.comments)
            else:
                raise('inst must be a list of Evokeds or an Epochs object')
        # keep variables
        self.signals_ = np.squeeze(signals, axis=1)
        self.times_ = np.squeeze(times, axis=1)
        self.comments_ = np.squeeze(comments, axis=1)
        self.pos = pos # for plotting
        self.alpha = alpha
        self.p_threshold = p_threshold
        self.t_threshold = t_threshold
        self.connectivity = connectivity
        self.n_jobs = n_jobs
        self.stats()
        return

    def stats(self):
        """"""
        from scipy import stats as stats
        from mne.stats import (spatio_temporal_cluster_1samp_test,
                               summarize_clusters_stc)
        from mne.channels import read_ch_connectivity

        # check dimensionality
        if len(self.signals_) != 2:
            raise('paired test should only have two datasets')
        if np.shape(self.signals_[0]) != np.shape(self.signals_[1]):
            raise('The dimensionality of the two datasets must be identical')
        n_subjects = np.shape(self.signals_[0])[0]

        # Apply contrast: n * space * time
        X = np.array(self.signals_[0] - self.signals_[1]).transpose([0, 2, 1])

        if self.t_threshold is None:
            self.t_threshold = -stats.distributions.t.ppf(self.p_threshold / 2.,
                                                          n_subjects - 1)

        # load FieldTrip neighbor definition to setup sensor connectivity
        if type(self.connectivity) is str:
            connectivity, ch_names = read_ch_connectivity(self.connectivity)

        # Run stats
        self.T_obs_, self.clusters_, self.cluster_p_values_, self.H0_ = clu = \
            spatio_temporal_cluster_1samp_test(X, connectivity=connectivity,
                                               n_jobs=self.n_jobs,
                                               threshold=self.t_threshold)
        # Save cluster indices
        self.good_cluster_inds_ = np.where(self.cluster_p_values_ < self.alpha)[0]
        return

    def plot_cluster_topo(self, i_clu=0, fig=None, ax=None, show=True):
        """"""
        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from mne.viz import plot_topomap, tight_layout

        #  XXX default: takes times of first cond
        times = self.times_[0] * 1000

        # unpack cluster infomation, get unique indices
        time_inds, space_inds = np.squeeze(self.clusters_[self.good_cluster_inds_[i_clu]])
        ch_inds = np.unique(space_inds)
        time_inds = np.unique(time_inds)

        # get topography for F stat
        f_map = self.T_obs_[time_inds, ...].mean(axis=0)

        # significant time
        sig_times = times[time_inds]

        # create spatial mask
        mask = np.zeros((f_map.shape[0], 1), dtype=bool)
        mask[ch_inds, :] = True

        # initialize figure
        if fig is None:
            fig = plt.figure()
        if ax is None:
            ax = fig.add_subplot(111)

        title = 'Cluster #{0}'.format(i_clu)
        ax.set_title(title, fontsize=14)

        # plot average test statistic and mark significant sensors
        image, _ = plot_topomap(f_map, self.pos, mask=mask, axis=ax,
                                cmap='binary', vmin=np.min, vmax=np.max)

        # advanced matplotlib for showing image with figsure and colorbar
        # in one plot
        divider = make_axes_locatable(ax)

        ax.set_xlabel('Averaged F-map ({:0.1f} - {:0.1f} s)'.format(
                           *sig_times[[0, -1]]))
        # add axes for colorbar
        ax_colorbar = divider.append_axes('right', size='5%', pad=0.05)
        plt.colorbar(image, cax=ax_colorbar)

        if show:
            plt.show()
        return fig

    def plot_evoked_time(self, i_clu=0, linestyles=None, condition_names=None,
                          colors=None, fig=None, ax=None, show=True):
        """"""
        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from mne.viz import plot_topomap, tight_layout

        if condition_names is None:
            condition_names = [c for c in self.comments_]
        if colors is None:
            colors = 'r', 'steelblue'  # XXX adapt for more than 2 conditions
        if linestyles is None:
            linestyles = '-', '-' # XXX adapt for more than 2 conditions

        #  XXX default: takes times of first cond
        times = self.times_[0] * 1000

        # unpack cluster infomation, get unique indices
        time_inds, space_inds = np.squeeze(self.clusters_[self.good_cluster_inds_[i_clu]])
        ch_inds = np.unique(space_inds)
        time_inds = np.unique(time_inds)

        # get average signals at significant sensors
        avgs = [x[..., ch_inds].mean(axis=-1) for x in self.signals_]
        sig_times = times[time_inds]

        # initialize figure
        if fig is None:
            fig = plt.figure()
        if ax is None:
            ax = fig.add_subplot(111)

        # add new axis for time courses and plot time courses
        for signal, col, ls in zip(self.signals_, colors, linestyles):
            signal = np.mean(signal, axis=0).transpose()
            ax.plot(times, signal, color=col, linestyle=ls)

        # add information
        ax.axvline(0, color='k', linestyle=':', label='stimulus onset')
        ax.set_xlim([times[0], times[-1]])
        ax.set_xlabel('Time [ms]')
        ax.set_ylabel('Evoked magnetic fields [fT]')

        # plot significant time range
        ymin, ymax = ax.get_ylim()
        ax.fill_betweenx((ymin, ymax), sig_times[0], sig_times[-1],
                                 color='orange', alpha=0.3)
        ax.legend(loc='lower right')
        ax.set_ylim(ymin, ymax)

        if show:
            plt.show()
        return fig

    def plot_cluster_time(self, i_clu=0, linestyles=None, condition_names=None,
                          colors=None, fig=None, ax=None, show=True):
        """"""
        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from mne.viz import plot_topomap, tight_layout

        if condition_names is None:
            condition_names = [c for c in self.comments_]
        if colors is None:
            colors = 'r', 'steelblue'  # XXX adapt for more than 2 conditions
        if linestyles is None:
            linestyles = '-', '-' # XXX adapt for more than 2 conditions

        #  XXX default: takes times of first cond
        times = self.times_[0] * 1000

        # unpack cluster infomation, get unique indices
        time_inds, space_inds = np.squeeze(self.clusters_[self.good_cluster_inds_[i_clu]])
        ch_inds = np.unique(space_inds)
        time_inds = np.unique(time_inds)

        # initialize figure
        if fig is None:
            fig = plt.figure()
        if ax is None:
            ax = fig.add_subplot(111)

        # get average signals of the cluster for each condition
        avgs = [x[:, ch_inds, :].mean(axis=1).mean(axis=0) for x in self.signals_]
        sig_times = times[time_inds]

        # add new axis for time courses and plot time courses
        for signal, col, ls in zip(avgs, colors, linestyles):
            ax.plot(times, signal, color=col, linestyle=ls)

        # add information
        ax.axvline(0, color='k', linestyle=':', label='stimulus onset')
        ax.set_xlim([times[0], times[-1]])
        ax.set_xlabel('Time [ms]')
        ax.set_ylabel('Evoked magnetic fields [fT]')

        # plot significant time range
        ymin, ymax = ax.get_ylim()
        ax.fill_betweenx((ymin, ymax), sig_times[0], sig_times[-1],
                                 color='orange', alpha=0.3)
        ax.legend(loc='lower right')
        ax.set_ylim(ymin, ymax)

        if show:
            plt.show()
        return fig


    def plot(self, colors=None, linestyles=None, condition_names=None, show=True):
        """"""
        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from mne.viz import plot_topomap, tight_layout

        if condition_names is None:
            condition_names = [c for c in self.comments_]
        if colors is None:
            colors = 'r', 'steelblue'  # XXX adapt for more than 2 conditions
        if linestyles is None:
            linestyles = '-', '--' # XXX adapt for more than 2 conditions

        #  XXX default: takes times of first cond
        times = self.times_[0]
        # loop over significant clusters
        figs = [list() for i in range(len(self.good_cluster_inds_))]
        for i_clu, clu_idx in enumerate(self.good_cluster_inds_):
            figs[i_clu], ax_topo = plt.subplots(1, 1, figsize=(10, 3))

            # topo
            self.plot_cluster_topo(i_clu, fig=figs[i_clu], ax=ax_topo, show=False)

            # time signals
            divider = make_axes_locatable(ax_topo)
            ax_signals = divider.append_axes('right', size='300%', pad=1.2)
            self.plot_cluster_time(i_clu, fig=figs[i_clu], ax=ax_signals, show=False)

            # clean up viz
            tight_layout(fig=figs[i_clu])
            figs[i_clu].subplots_adjust(bottom=.05)

        if show:
            plt.show()
        return figs

    def plot_evoked_time(self, plot_diff=True, linestyles=None,
                         condition_names=None,
                         colors=None, fig=None, ax=None, show=True):
        """"""
        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from mne.viz import plot_topomap, tight_layout

        if condition_names is None:
            condition_names = [c for c in self.comments_]
        if colors is None:
            colors = 'r', 'steelblue'  # XXX adapt for more than 2 conditions
        if linestyles is None:
            linestyles = '-', '-' # XXX adapt for more than 2 conditions

        #  XXX default: takes times of first cond
        times = self.times_[0] * 1000

                # initialize figure
        if fig is None:
            fig = plt.figure()
        if ax is None:
            ax = fig.add_subplot(111)

        # get average signals of the cluster for each condition
        avgs = [x[:, :, :].mean(axis=0) for x in self.signals_]

        if not(plot_diff):
            # add new axis for time courses and plot time courses
            for signal, col, ls in zip(avgs, colors, linestyles):
                for ch in signal:
                    ax.plot(times, ch, color=col, linestyle=ls)
        else:
            # add new axis for time courses and plot time courses
            avgs = avgs[0] - avgs[1]
            for ch in avgs:
                ax.plot(times, ch, color='black', linestyle='-')

        # add information
        ax.axvline(0, color='k', linestyle=':', label='stimulus onset')
        ax.set_xlim([times[0], times[-1]])
        ax.set_xlabel('Time [ms]')
        ax.set_ylabel('Evoked magnetic fields [fT]')

        # plot significant time range
        ymin, ymax = ax.get_ylim()
        for cluster in self.good_cluster_inds_:
            # unpack cluster infomation, get unique indices
            time_inds, space_inds = np.squeeze(self.clusters_[cluster]) # XXX
            ch_inds = np.unique(space_inds)
            time_inds = np.unique(time_inds)
            sig_times = times[time_inds]
            ax.fill_betweenx((ymin, ymax), sig_times[0], sig_times[-1],
                                 color='orange', alpha=0.3)
        ax.legend(loc='lower right')
        ax.set_ylim(ymin, ymax)

        if show:
            plt.show()
        return fig
