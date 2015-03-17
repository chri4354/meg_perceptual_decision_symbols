import os
subjects = ['subject01_ar', 'subject02_as', 'subject03_rm', 'subject04_jm',
      'subject05_cl', 'subject06_ha', 'subject07_sb', 'subject08_pj',
      'subject09_kr', 'subject10_cs', 'subject11_aj', 'subject12_ea',
      'subject13_cg', 'subject14_ap', 'subject15_tb', 'subject16_mc',
      'subject17_az']

for subject in subjects:
  os.mkdir('/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/mri/' + subject)
