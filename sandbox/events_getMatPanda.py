import pandas as pd
from ambiguity.conditions import get_events

bhv_fname   = '/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/behavior/cl_behaviorMEG.mat'
events = get_events(bhv_fname)


df = pd.DataFrame(events)
