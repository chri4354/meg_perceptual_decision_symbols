cd('/media/harddrive/2013_meg_ambiguity/python/')

try:
    run scripts/run_filtering.py
except (RuntimeError, TypeError, NameError):
    print('Error Filtering')

try:
    run scripts/run_ica.py
except (RuntimeError, TypeError, NameError):
        print('Error ICA')

try:
    run scripts/run_extract_events.py
except (RuntimeError, TypeError, NameError):
    print('Error Events')

try:
    run scripts/run_extract_epochs.py
except (RuntimeError, TypeError, NameError):
    print('Error Epochs')
