

    # decoding
    letter = np.where(events.get('stim_category')==1)[0]
    digit = np.where(events.get('stim_category')==8)[0]

    y = events.get('stim_category')
    sel = np.where((y==1) | (y==8))[0]
    gat = GeneralizationAcrossTime(cv=4, n_jobs=-1)
    gat.fit(epochs[sel], y=y[sel])
    gat.score(epochs[sel], y=y[sel])
    gat.plot(vmin=0.4, vmax=0.6)
